from flask import Flask, request, jsonify
from services.task_handlers import TASK_HANDLERS
from services.task_tree import build_task_tree, execute_task_tree
from services.prompt_builder import build_prompt, build_error_prompt
from werkzeug.exceptions import RequestEntityTooLarge
from logger import LOGGER
import asyncio

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

@app.errorhandler(RequestEntityTooLarge)
def handle_large_request(e):
    return jsonify({"error": "Request too large"}), 413

@app.route("/tasks", methods=["POST"])
async def process_tasks():
    try:
        if not request.is_json:
            LOGGER.warning("Non-JSON request received")
            return build_error_prompt("Request content type must be application/json"), 400
            
        data = request.get_json()

        # Validate and log session_id
        session_id = data.get("session_id")
        if not session_id:
            return build_error_prompt("Missing session_id"), 400
        LOGGER.info(f"Processing tasks for session: {session_id}")

        if not data or "request" not in data or "tasks" not in data["request"]:
            LOGGER.warning("Invalid request format received")
            return build_error_prompt("Invalid request format"), 400
            
        tasks = data["request"]["tasks"]
        if not isinstance(tasks, list) or not tasks:
            LOGGER.warning("Invalid tasks format or empty tasks list")
            return build_error_prompt("Tasks must be a non-empty array"), 400
            
        # Validate the format of each task
        for task in tasks:
            if not isinstance(task, dict) or "type" not in task or "id" not in task:
                LOGGER.warning(f"Invalid task format: {task}")
                return build_error_prompt("Each task must include 'type' and 'id'", f"Invalid task: {task}"), 400
            
            if task["type"] == "end":
                return "Session ended", 200
        
        # Build the task tree from the list of tasks
        root_nodes = await build_task_tree(tasks)
        # Execute the task tree and collect results
        results = await execute_task_tree(root_nodes, lambda task: TASK_HANDLERS[task.type](task))
        # Build the prompt based on the results
        prompt = build_prompt(results)
        return prompt, 200
    except ValueError as e:
        return build_error_prompt(str(e)), 400
    except Exception as e:
        LOGGER.error(f"Unexpected error: {str(e)}")
        return build_error_prompt("Internal server error"), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)

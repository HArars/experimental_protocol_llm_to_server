import logging
import os

logger = logging.getLogger(__name__)

def load_template(file_path):
    try:
        # Check if the template file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file not found: {file_path}")
        # Read and return the content of the template file
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # Log any error that occurs during the loading of the template
        logger.error(f"Error loading template: {str(e)}")
        raise

def build_prompt(results, template_path="templates/prompt_template.txt"):
    # Load the template content
    template = load_template(template_path)
    # Build the task details string from the results
    task_details = "\n".join(
        [f"  - Task {r['id']} ({r['type']}): {'Success' if r['success'] else 'Failed'}. {r['description']}"
         for r in results]
    )
    # Determine if all tasks were successful
    all_success = all(r["success"] for r in results)
    # Create a summary based on the success of all tasks
    summary = "All tasks completed successfully." if all_success else "Some tasks failed."
    # Determine the next steps based on the success of all tasks
    next_steps = (
        "You may now proceed with the next steps. Send a new JSON command or type 'end' to finish."
        if all_success else
        "Please review the errors and send corrections."
    )
    # Replace placeholders in the template with actual values
    return template.replace("{{TASK_DETAILS}}", task_details) \
        .replace("{{SUMMARY}}", summary) \
        .replace("{{NEXT_STEPS}}", next_steps)

def build_error_prompt(error_message, task_details="", template_path="templates/error_template.txt"):
    # Load the error template content
    template = load_template(template_path)
    # Replace placeholders in the template with actual error message and task details
    return template.replace("{{ERROR_MESSAGE}}", error_message).replace("{{TASK_DETAILS}}", task_details)

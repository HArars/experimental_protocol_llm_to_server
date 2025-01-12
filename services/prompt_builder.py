import logging
import os

logger = logging.getLogger(__name__)

def load_template(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        raise

def build_prompt(results, template_path="templates/prompt_template.txt"):
    template = load_template(template_path)
    task_details = "\n".join(
        [f"  - Task {r['id']} ({r['type']}): {'Success' if r['success'] else 'Failed'}. {r['description']}"
         for r in results]
    )
    all_success = all(r["success"] for r in results)
    summary = "All tasks completed successfully." if all_success else "Some tasks failed."
    next_steps = (
        "You may now proceed with the next steps. Send a new JSON command or type 'end' to finish."
        if all_success else
        "Please review the errors and send corrections."
    )
    return template.replace("{{TASK_DETAILS}}", task_details) \
        .replace("{{SUMMARY}}", summary) \
        .replace("{{NEXT_STEPS}}", next_steps)

def build_error_prompt(error_message, task_details="", template_path="templates/error_template.txt"):
    template = load_template(template_path)
    return template.replace("{{ERROR_MESSAGE}}", error_message).replace("{{TASK_DETAILS}}", task_details)

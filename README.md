# ProtocolLLM

ProtocolLLM is a Python-based framework for handling terminal-PC communication for the Large Language Model (LLM) protocol. It provides a standardized interface for managing tasks, executing commands, and handling session-based interactions.

An **experimental !!** LLM-PC protocol

## Request a template

```json
{
  "session_id": "session_56789",
  "request": {
    "tasks": [
      {
        "id": 1,
        "type": "write",
        "parameters": {
          "path": "/path/to/file1.txt",
          "content": "This is the content of file1."
        },
        "execution_order": 1
      },
      {
        "id": 2,
        "type": "read",
        "parameters": {
          "path": "/path/to/file1.txt"
        },
        "depends_on": [1],
        "execution_order": 2
      },
      {
        "id": 3,
        "type": "exec",
        "parameters": {
          "command": "pip --version"
        },
        "depends_on": [2],
        "execution_order": 3
      }
    ]
  }
}
```

## Response templates

```txt
Hello!

Here are the tasks we processed for you:

{{TASK_DETAILS}}

Overall Result:
{{SUMMARY}}

Next Steps:
{{NEXT_STEPS}}

Thank you for using our service.
```


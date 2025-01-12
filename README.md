# Protocol LLM

ProtocolLLM is a Python-based framework for handling terminal-PC communication for the Large Language Model (LLM) protocol. 

An **experimental !!** LLM-PC protocol

## LLM Request

```http
POST http://localhost:3000/tasks
Content-Type: application/json

{
  "session_id": "session_56789",
  "request": {
    "tasks": [
      {
        "id": 1,
        "type": "write",
        "parameters": {
          "path": "test/test_tasks/file1.txt",
          "content": "This is the content of file1."
        },
        "execution_order": 1
      },
      {
        "id": 3,
        "type": "read",
        "parameters": {
          "path": "test/test_tasks/file1.txt"
        },
        "depends_on": [2],
        "execution_order": 3
      },
      {
        "id": 2,
        "type": "exec",
        "parameters": {
          "command": "npm --version"
        },
        "depends_on": [1],
        "execution_order": 2
      }
    ]
  }
}
```

## Server Response

```txt
HTTP/1.1 200 OK
Server: Werkzeug/2.3.7 Python/3.12.8
Date: Sun, 12 Jan 2025 11:00:48 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 531
Connection: close

Hello!

Here are the tasks we processed for you:

  - Task 1 (write): Success. File 'test/test_tasks/file1.txt' written successfully
  - Task 2 (exec): Success. Command 'npm --version' executed successfully. Output: 10.9.0

  - Task 3 (read): Success. File 'test/test_tasks/file1.txt' read successfully. Content: This is the content of file1.

Overall Result:
All tasks completed successfully.

Next Steps:
You may now proceed with the next steps. Send a new JSON command or type 'end' to finish.

Thank you for using our service.
```


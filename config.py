# filepath: config.py
import os

# Base directory configuration
BASE_DIR = os.getenv("APP_BASE_DIR", os.path.dirname(os.path.dirname(__file__)))

# File size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed commands whitelist
ALLOWED_COMMANDS = [
    "git",
    "pip",
    "cat",
    "type",
    "npm",
    "yarn",
    "pnpm",
    "conda",
    "echo"
]

# Log directory path
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

import os
import shlex
import subprocess
from utils.file_utils import ensure_directory_exists, is_safe_path
from config import BASE_DIR, MAX_FILE_SIZE, ALLOWED_COMMANDS  # Import constants
from logger import LOGGER

class TaskConfig:
    BASE_DIR = BASE_DIR
    MAX_FILE_SIZE = MAX_FILE_SIZE
    ALLOWED_COMMANDS = ALLOWED_COMMANDS

def execute_command(command, timeout=60, cwd=None):
    """
    Execute shell command and get real-time output
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        cwd: Working directory
    
    Returns:
        str: Command execution output
    """
    try:
        # Get system PATH
        env = os.environ.copy()

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env
        )

        stdout_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                stdout_lines.append(output)
                LOGGER.info(f"Command output: {output.strip()}")

        process.wait(timeout=timeout)
        stdout_result = "".join(stdout_lines)
        
        if process.returncode != 0:
            stderr = process.stderr.read()
            raise subprocess.CalledProcessError(process.returncode, command, stdout_result, stderr)
            
        return stdout_result

    except subprocess.TimeoutExpired:
        process.kill()
        raise


async def handle_write(task):
    """Handle file write task"""
    try:
        path = task.parameters.get("path")
        content = task.parameters.get("content")
        mode = task.parameters.get("mode", "w")
        
        LOGGER.info(f"Handling write task for path: {path}")
        
        if not is_safe_path(TaskConfig.BASE_DIR, path):
            LOGGER.warning(f"Invalid file path attempt: {path}")
            raise ValueError("Invalid file path")
        
        if len(content.encode()) > TaskConfig.MAX_FILE_SIZE:
            raise ValueError("Content too large")
        
        if not path:
            raise ValueError("Write task requires 'path'")
        if content is None:
            raise ValueError("Write task requires 'content'")
        
        await ensure_directory_exists(TaskConfig.BASE_DIR, path)
        
        try:
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Failed to write to file '{path}': {str(e)}")
            
        return f"File '{path}' written successfully"
    
    except Exception as e:
        LOGGER.error(f"Write operation failed: {str(e)}")
        raise

async def handle_read(task):
    """
    Handle file read task.
    :param task: dict containing task details
    :return: str success description
    """
    # Get task parameters
    path = task.parameters.get("path")

    # Check required parameters
    if not path:
        raise ValueError("Read task requires 'path'.")

    if not is_safe_path(TaskConfig.BASE_DIR, path):
        LOGGER.warning(f"Unauthorized read attempt: {path}")
        raise ValueError("Invalid file path")

    # Check if file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' not found.")

    # Read file
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Failed to read from file '{path}': {str(e)}")

    return f"File '{path}' read successfully. Content: {content}"

def is_command_allowed(command):
    """Verify if command is in whitelist"""
    cmd = shlex.split(command)[0]
    return cmd in TaskConfig.ALLOWED_COMMANDS

async def handle_exec(task):
    """Handle command execution task"""
    try:
        command = task.parameters.get("command")
        timeout = min(task.parameters.get("timeout", 60), 120)  # Maximum 5 minutes
        
        LOGGER.info(f"Handling exec task with command: {command}")
        
        if not command or not is_command_allowed(command):
            LOGGER.warning(f"Unauthorized command attempt: {command}")
            raise ValueError("Command not allowed")
        
        # Print current working directory and command to execute
        current_directory = os.getcwd()
        LOGGER.info(f"Current working directory: {current_directory}")
        LOGGER.info(f"Executing command: {command}")
        
        safe_command = shlex.split(command)
        LOGGER.warning(f"safe_command: {safe_command}")
        # result = subprocess.run(
        #     # safe_command,
        #     command,
        #     text=True,
        #     shell=True,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     # check=False,
        #     # timeout=timeout,
        #     cwd=TaskConfig.BASE_DIR,
        #     # env={},  # Clear environment variables
        # )
        stdout = execute_command(command, timeout, TaskConfig.BASE_DIR)
        return f"Command '{command}' executed successfully. Output: {stdout}"
    except subprocess.TimeoutExpired:
        LOGGER.error(f"Command timed out after {timeout} seconds")
        raise RuntimeError("Command execution timed out")
    except Exception as e:
        LOGGER.error(f"Command execution failed: {str(e)}")
        raise e

async def handle_delete(task):
    """Handle file deletion task"""
    try:
        path = task.parameters.get("path")
        
        LOGGER.info(f"Handling delete task for path: {path}")
        
        # Check required parameters
        if not path:
            raise ValueError("Delete task requires 'path'")
            
        # Safety check
        if not is_safe_path(TaskConfig.BASE_DIR, path):
            LOGGER.warning(f"Invalid file path attempt: {path}")
            raise ValueError("Invalid file path")
            
        # Check if file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{path}' not found")
            
        # Delete file
        try:
            os.remove(path)
        except Exception as e:
            raise IOError(f"Failed to delete file '{path}': {str(e)}")
            
        return f"File '{path}' deleted successfully"
        
    except Exception as e:
        LOGGER.error(f"Delete operation failed: {str(e)}")
        raise

async def handle_move(task):
    """Handle file move task"""
    try:
        source = task.parameters.get("source")
        destination = task.parameters.get("destination")
        
        LOGGER.info(f"Handling move task from {source} to {destination}")
        
        # Check required parameters
        if not source or not destination:
            raise ValueError("Move task requires 'source' and 'destination'")
            
        # Safety check
        if not is_safe_path(TaskConfig.BASE_DIR, source) or not is_safe_path(TaskConfig.BASE_DIR, destination):
            LOGGER.warning(f"Invalid file path attempt: {source} or {destination}")
            raise ValueError("Invalid file path")
            
        # Check if source file exists
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source file '{source}' not found")
            
        # Ensure destination directory exists
        ensure_directory_exists(TaskConfig.BASE_DIR, destination)
        
        # Move file
        try:
            os.rename(source, destination)
        except Exception as e:
            raise IOError(f"Failed to move file from '{source}' to '{destination}': {str(e)}")
            
        return f"File moved from '{source}' to '{destination}' successfully"
        
    except Exception as e:
        LOGGER.error(f"Move operation failed: {str(e)}")
        raise

async def handle_copy(task):
    """Handle file copy task"""
    try:
        src_path = task.parameters.get("source")
        dst_path = task.parameters.get("destination")
        
        if not src_path or not dst_path:
            raise ValueError("Copy task requires both 'source' and 'destination' paths")
            
        if not is_safe_path(TaskConfig.BASE_DIR, src_path) or not is_safe_path(TaskConfig.BASE_DIR, dst_path):
            raise ValueError("Invalid file path")
            
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source file '{src_path}' not found")
            
        ensure_directory_exists(TaskConfig.BASE_DIR, os.path.dirname(dst_path))
        
        import shutil
        shutil.copy2(src_path, dst_path)
        
        return f"File copied from '{src_path}' to '{dst_path}' successfully"
        
    except Exception as e:
        LOGGER.error(f"Copy operation failed: {str(e)}")
        raise

async def handle_list(task):
    """Handle directory listing task"""
    try:
        path = task.parameters.get("path", ".")
        recursive = task.parameters.get("recursive", False)
        
        if not is_safe_path(TaskConfig.BASE_DIR, path):
            raise ValueError("Invalid directory path")
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory '{path}' not found")
            
        result = []
        if recursive:
            for root, dirs, filenames in os.walk(path):
                rel_path = os.path.relpath(root, path)
                if rel_path == ".":
                    prefix = ""
                else:
                    prefix = rel_path + "/"
                    
                # Add directories
                for d in dirs:
                    result.append(f"📁 {prefix}{d}/")
                    
                # Add files
                for f in filenames:
                    result.append(f"📄 {prefix}{f}")
        else:
            entries = os.listdir(path)
            for entry in sorted(entries):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    result.append(f"📁 {entry}/")
                else:
                    result.append(f"📄 {entry}")
                    
        if not result:
            return f"Directory '{path}' is empty"
            
        files_str = "\n".join(sorted(result))
        return f"Contents of directory '{path}':\n{files_str}"
            
    except Exception as e:
        LOGGER.error(f"List operation failed: {str(e)}")
        raise

async def handle_mkdir(task):
    """Handle directory creation task"""
    try:
        path = task.parameters.get("path")
        
        LOGGER.info(f"Handling mkdir task for path: {path}")
        
        # Check required parameters
        if not path:
            raise ValueError("Mkdir task requires 'path'")
            
        # Safety check
        if not is_safe_path(TaskConfig.BASE_DIR, path):
            LOGGER.warning(f"Invalid directory path attempt: {path}")
            raise ValueError("Invalid directory path")
        
        # Check if directory already exists
        if os.path.exists(path):
            LOGGER.info(f"Directory '{path}' already exists")
            return f"Directory '{path}' already exists"
            
        # Create directory
        try:
            os.makedirs(path)
            # Verify if directory was created successfully
            if os.path.exists(path) and os.path.isdir(path):
                LOGGER.info(f"Directory '{path}' created successfully")
                return f"Directory '{path}' created successfully"
            else:
                raise IOError(f"Failed to verify directory creation: {path}")
        except Exception as e:
            raise IOError(f"Failed to create directory '{path}': {str(e)}")
            
    except Exception as e:
        LOGGER.error(f"Mkdir operation failed: {str(e)}")
        raise

# Task handler mapping
TASK_HANDLERS = {
    "write": handle_write,
    "read": handle_read,
    "exec": handle_exec,
    "delete": handle_delete,  # Add delete handler
    "move": handle_move,  # Add move handler
    "copy": handle_copy,
    "list": handle_list,
    "mkdir": handle_mkdir,  # Add mkdir handler
}
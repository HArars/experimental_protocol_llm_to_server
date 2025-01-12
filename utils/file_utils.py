import os
from pathlib import Path
import asyncio

def is_safe_path(base_dir, path):
    """Verify if the file path is safe"""
    try:
        base_path = Path(base_dir).resolve()
        file_path = Path(base_dir).joinpath(path).resolve()
        return file_path.relative_to(base_path)
    except (TypeError, ValueError):
        return False

async def ensure_directory_exists(base_dir, path):
    """Safely ensure the directory exists"""
    if not is_safe_path(base_dir, path):
        raise ValueError("Invalid path")
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        await asyncio.to_thread(os.makedirs, directory, exist_ok=True)

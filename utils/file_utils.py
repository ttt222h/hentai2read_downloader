import re
import os

def sanitize_filename(name: str, replace_char: str = "_") -> str:
    """
    Sanitizes a string to be used as a filename or directory name.
    Replaces invalid characters with a specified replacement character.
    """
    # Define invalid characters for Windows and Unix-like systems
    # Windows invalid characters: < > : " / \ | ? *
    # Unix-like invalid characters: / (and null byte)
    # Also, control characters are generally invalid.
    invalid_chars_pattern = r'[<>:"/\\|?*\x00-\x1F]'
    
    # Replace invalid characters
    sanitized_name = re.sub(invalid_chars_pattern, replace_char, name)
    
    # Remove leading/trailing spaces and periods (problematic on Windows)
    sanitized_name = sanitized_name.strip(" .")
    
    # Ensure the name is not empty after sanitization
    if not sanitized_name:
        return "untitled" + replace_char + "file"

    return sanitized_name

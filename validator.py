import re

def valid_task_name(text):
    pattern = r"^[a-zA-Z0-9\s\-]{2,50}$"
    return bool(re.fullmatch(pattern, text.strip()))
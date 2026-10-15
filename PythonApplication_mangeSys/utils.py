import re

def check_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    if re.match(pattern, phone):
        return True
    return False

import os
import subprocess

def vulnerable_function(user_input):
    # Security issue: SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"

    # Security issue: Command injection
    os.system("ls " + user_input)

    # Bug: Potential division by zero
    result = 100 / 0

    # Code quality: unused variable
    unused_var = "this is not used"

    return query

def another_function():
    # Bug: undefined variable
    return undefined_variable

# Missing docstring and type hints
def process_data(data):
    if data == None:  # Should use 'is None'
        return []
    return data.split(",")

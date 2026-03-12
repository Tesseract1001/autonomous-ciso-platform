# ============================================================
# INTENTIONALLY VULNERABLE PYTHON FILE — FOR TESTING PURPOSES
# This file is a demo to show how the scanner catches real bugs.
# DO NOT use this code in production!
# ============================================================

import os
import subprocess
import sqlite3
import pickle
import hashlib

# --- VULNERABILITY 1: Hardcoded credentials ---
DATABASE_PASSWORD = "SuperSecret123!"
API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# --- VULNERABILITY 2: SQL Injection ---
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: String formatting in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# --- VULNERABILITY 3: Command Injection ---
def ping_server(host):
    # BAD: User input directly in shell command
    result = subprocess.call(f"ping -c 4 {host}", shell=True)
    return result

# --- VULNERABILITY 4: Insecure deserialization ---
def load_user_session(session_data):
    # BAD: Loading untrusted pickle data
    return pickle.loads(session_data)

# --- VULNERABILITY 5: Use of eval ---
def calculate(expression):
    # BAD: eval on user input
    return eval(expression)

# --- VULNERABILITY 6: Weak hashing ---
def hash_password(password):
    # BAD: MD5 is broken for password hashing
    return hashlib.md5(password.encode()).hexdigest()

# --- VULNERABILITY 7: Hardcoded JWT ---
JWT_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# --- VULNERABILITY 8: Debug mode / assert ---
DEBUG_MODE = True
assert DEBUG_MODE, "Debug should be on"

def admin_panel():
    # BAD: No authentication check
    if DEBUG_MODE:
        return "Welcome to admin panel! Here are all user records..."
    
# --- VULNERABILITY 9: Exec usage ---
def run_plugin(plugin_code):
    exec(plugin_code)

if __name__ == "__main__":
    print("This is an intentionally vulnerable demo file.")
    print(f"DB Password: {DATABASE_PASSWORD}")
    user = get_user("admin' OR '1'='1")
    print(user)

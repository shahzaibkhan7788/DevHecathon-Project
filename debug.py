import os
import sys

print(f"Python: {sys.executable}")
print(f"CWD: {os.getcwd()}")

# Apply the same patch as app.py
git_path = r"C:\Program Files\Git\bin\git.exe"
if not os.path.exists(git_path):
    git_path = r"C:\Program Files\Git\cmd\git.exe"
if not os.path.exists(git_path):
    git_path = r"C:\Users\Yeagerist\AppData\Local\Programs\Git\bin\git.exe"

print(f"Found git at: {git_path}")
if os.path.exists(git_path):
    os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = git_path

try:
    import git
    print("SUCCESS: import git")
except Exception as e:
    print(f"FAIL: import git - {e}")

try:
    import db
    print("SUCCESS: import db")
except Exception as e:
    print(f"FAIL: import db - {e}")

try:
    import ingestion
    print(f"SUCCESS: import ingestion (Attributes: {dir(ingestion)})")
except Exception as e:
    print(f"FAIL: import ingestion - {e}")

try:
    from ingestion import ingest_repo
    print("SUCCESS: from ingestion import ingest_repo")
except Exception as e:
    print(f"FAIL: from ingestion import ingest_repo - {e}")

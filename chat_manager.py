import os
import json

CHAT_DIR = "./chats"

def ensure_chat_dir(username):
    user_dir = os.path.join(CHAT_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def get_chat_file(username: str, repo_name: str):
    user_dir = ensure_chat_dir(username)
    # Sanitize repo name for filename
    safe_name = repo_name.replace("/", "_").replace("\\", "_").replace(":", "")
    return os.path.join(user_dir, f"{safe_name}.json")

def save_chat_history(username: str, repo_name: str, messages: list):
    """Saves the current chat history for a repo and user."""
    if not username: return
    try:
        filepath = get_chat_file(username, repo_name)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history(username: str, repo_name: str):
    """Loads chat history for a repo and user."""
    if not username: return []
    
    # Try new user-specific location first
    filepath = get_chat_file(username, repo_name)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []
    
    # Fallback: check old location (for backward compatibility)
    safe_name = repo_name.replace("/", "_").replace("\\", "_").replace(":", "")
    old_filepath = os.path.join(CHAT_DIR, f"{safe_name}.json")
    if os.path.exists(old_filepath):
        try:
            with open(old_filepath, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # Migrate to new location
                save_chat_history(username, repo_name, messages)
                return messages
        except Exception as e:
            print(f"Error loading old chat history: {e}")
            return []
    
    return []

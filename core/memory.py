import json
import os

MEMORY_FILE = "jarvis_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def remember(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)

def recall(key):
    data = load_memory()
    return data.get(key, None)

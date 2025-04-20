import json, os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"users": {}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def init_user(user_id, username):
    memory = load_memory()
    users = memory["users"]
    if user_id not in users:
        users[user_id] = {
            "name": username,
            "facts": [],
            "topics": [],
            "likes": [],
            "last_message": ""
        }
        save_memory(memory)

def remember_fact(user_id, fact):
    memory = load_memory()
    user = memory["users"][user_id]
    if fact not in user["facts"]:
        user["facts"].append(fact)
        save_memory(memory)

def remember_like(user_id, thing):
    memory = load_memory()
    user = memory["users"][user_id]
    if thing not in user["likes"]:
        user["likes"].append(thing)
        save_memory(memory)

def update_topic(user_id, topic):
    memory = load_memory()
    user = memory["users"][user_id]
    user["topics"].append(topic)
    user["topics"] = user["topics"][-5:]  # Nur die letzten 5
    save_memory(memory)

def get_user_profile(user_id):
    memory = load_memory()
    return memory["users"].get(user_id, {})


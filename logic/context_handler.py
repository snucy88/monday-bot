import time

# Global states (ja, dirty, aber effektiv für einen Single-User-Bot)
last_user_id = None
last_interaction_timestamp = 0
CONVERSATION_TIMEOUT = 180  # 3 Minuten

FOLLOWUP_CUES = [
    "warum", "meinst du", "was meinst du", "findest du", "bist du", "du", "dein", 
    "deine", "was soll das", "antwort", "wie geht", "was sagst du", "wirklich"
]

def reset_context_if_new_user(user_id):
    global last_user_id, last_interaction_timestamp
    if user_id != last_user_id:
        last_user_id = None
        last_interaction_timestamp = 0

def update_context(user_id):
    global last_user_id, last_interaction_timestamp
    last_user_id = user_id
    last_interaction_timestamp = time.time()

def is_followup(user_id, message_content):
    now = time.time()
    if user_id == last_user_id and (now - last_interaction_timestamp) < CONVERSATION_TIMEOUT:
        return any(cue in message_content.lower() for cue in FOLLOWUP_CUES)
    return False
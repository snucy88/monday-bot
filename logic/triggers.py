TRIGGERS = [
    "hilfe", "wtf", "miau", "lebst du", "bist du da", 
    "antwort", "openai", "admin", "kaputt", "fehler", "montag"
]

def has_trigger(msg):
    return any(trigger in msg.lower() for trigger in TRIGGERS)
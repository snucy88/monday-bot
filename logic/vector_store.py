import os
import requests
import json
from logic.embedding import get_embedding

SUPABASE_URL = "https://jxddphiowqfvmtoguepv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4ZGRwaGlvd3Fmdm10b2d1ZXB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUxNTM0ODQsImV4cCI6MjA2MDcyOTQ4NH0.kCMAr3ltorJO_P94ueJDWcaP4TIDY7UdYNsZ_oNg4rI"
SUPABASE_TABLE = "conversation_embeddings"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def store_embedding(user_id, username, input_text):
    vector = get_embedding(input_text)

    payload = {
        "user_id": user_id,
        "username": username,
        "input": input_text,
        "embedding": vector
    }

    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=HEADERS,
            data=json.dumps(payload)
        )
        if res.status_code >= 300:
            print("[SUPABASE ERROR]", res.text)
        else:
            print("[SUPABASE] Embedding gespeichert.")
    except Exception as e:
        print("[SUPABASE EXCEPTION]", e)

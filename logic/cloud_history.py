import requests
import datetime
import os

SUPABASE_URL = "https://jxddphiowqfvmtoguepv.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4ZGRwaGlvd3Fmdm10b2d1ZXB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUxNTM0ODQsImV4cCI6MjA2MDcyOTQ4NH0.kCMAr3ltorJO_P94ueJDWcaP4TIDY7UdYNsZ_oNg4rI"
HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def add_to_history(user_id, username, message, reply):
    url = f"{SUPABASE_URL}/rest/v1/conversation_memory"
    payload = {
        "user_id": user_id,
        "username": username,
        "message": message,
        "reply": reply,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Supabase speichern fehlgeschlagen: {response.text}")


def get_last_response(user_id):
    url = f"{SUPABASE_URL}/rest/v1/conversation_memory?user_id=eq.{user_id}&order=timestamp.desc&limit=1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["reply"]
    else:
        print(f"[ERROR] Supabase laden fehlgeschlagen: {response.text}")
    return None

import os
import requests
import numpy as np
from logic.embedding import get_embedding

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

def search_similar_messages(user_id, query, top_k=3):
    embedding = get_embedding(query)
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/match_conversations",
        headers={
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "query_embedding": embedding,
            "match_count": top_k,
            "user_id_param": user_id
        }
    )

    if response.status_code != 200:
        print(f"[Fehler bei Vektor-Suche]: {response.text}")
        return []

    return [item["message"] for item in response.json()]

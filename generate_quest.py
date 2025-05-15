import requests
import json
from pprint import pprint


API_BASE_URL = "http://localhost:5000"

def generate_quests():
    url = f"{API_BASE_URL}/generate_quests"
    response = requests.post(url)
    if response.status_code == 200:
        print("✅ Quests generated successfully!")
        data = response.json()
        pprint(data)
        return data["quest_ids"]
    else:
        print(f"❌ Failed to generate quests: {response.status_code}")
        print(response.text)
        return []

def fetch_active_quests():
    
    
    import pytz
    import firebase_admin
    from firebase_admin import credentials, firestore


    cred = credentials.Certificate("plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")
    firebase_admin.initialize_app(cred)


    db = firestore.client()

    quests_ref = db.collection("Quests")
    active_quests = quests_ref.where("status", "==", "pending").stream()

    print("\n📋 Active Quests:")
    for quest in active_quests:
        quest_data = quest.to_dict()
        print(f"- ID: {quest.id}")
        print(f"  Type: {quest_data['type']}")
        print(f"  Plant ID: {quest_data['plant_id']}")
        print(f"  Assigned To: {quest_data['assigned_to']}")
        print(f"  Created At: {quest_data['created_at'].astimezone(pytz.UTC)}")
        print(f"  Verified: {quest_data['verified']}")
        print()

if __name__ == "__main__":
    generate_quests()
    fetch_active_quests()

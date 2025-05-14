import json
from app import app  # Make sure your Flask app is exposed as `app` in app.py

client = app.test_client()

def pretty_print(response):
    print(f"\n🔍 Status Code: {response.status_code}")
    try:
        data = response.get_json()
        print("📦 Response JSON:")
        print(json.dumps(data, indent=2))
    except Exception:
        print(response.data.decode())

def test_update_location():
    print("\n🧭 Testing: Update User Location")
    response = client.post("/user/location", json={
        "user_id": "uid234",
        "lat": 26.8467,
        "lng": 80.9462
    })
    pretty_print(response)

def test_nearby_quests():
    print("\n🌐 Testing: Fetch Nearby Quests")
    response = client.get("/quests/nearby", query_string={"user_id": "uid234"})
    pretty_print(response)

def test_adopt_plant():
    print("\n🌱 Testing: Adopt Plant")
    response = client.post("/user/adopt", json={
        "user_id": "uid234",
        "plant_id": "plant_3cddc792"
    })
    pretty_print(response)

def test_view_user_quests(status="pending"):
    print(f"\n📋 Testing: View User Quests [{status}]")
    response = client.get("/user/quests", query_string={
        "user_id": "uid234",
        "status": status
    })
    pretty_print(response)

def test_complete_quest():
    print("\n✅ Testing: Complete Quest")
    response = client.post("/user/complete_quest", json={
        "user_id": "uid123",
        "quest_id": "HVxh33jt9FsNX63GxhV6"
    })
    pretty_print(response)

# 🧪 Run the tests
if __name__ == "__main__":
    print("🚀 Running User API Integration Tests\n")

    test_update_location()
    test_nearby_quests()
    test_adopt_plant()
    test_view_user_quests("pending")
    test_complete_quest()
    test_view_user_quests("completed")

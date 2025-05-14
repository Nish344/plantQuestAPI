from datetime import datetime, timedelta
import pytz
import firebase_admin
from firebase_admin import credentials, firestore

# Use your downloaded service account key
cred = credentials.Certificate("plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")
firebase_admin.initialize_app(cred)

# ✅ CORRECT way to get the Firestore client
db = firestore.client()
now = datetime.now(pytz.UTC)
today_start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=pytz.UTC)

plants_ref = db.collection("Plants")
quests_ref = db.collection("Quests")
users_ref = db.collection("Users")

plants = plants_ref.stream()

now = datetime.now(pytz.UTC)
today_start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=pytz.UTC)

plants_ref = db.collection("Plants")
quests_ref = db.collection("Quests")
users_ref = db.collection("Users")

created_quests = []

plants = plants_ref.stream()
for plant_doc in plants:
    plant = plant_doc.to_dict()
    plant_id = plant_doc.id
    adopted_by = plant.get("adopted_by")
    last_watered = plant.get("last_watered")

    quest_types = {
        "Water Plant": {"frequency_days": 1},
        "Health Assessment": {"frequency_days": 3},
        "Growth Report": {"frequency_days": 3},
        "Photo Submission": {"frequency_days": 7}
    }

    for quest_type, config in quest_types.items():
        frequency = timedelta(days=config["frequency_days"])
        existing_quests = quests_ref \
            .where("plant_id", "==", plant_id) \
            .where("type", "==", quest_type) \
            .order_by("created_at", direction=firestore.Query.DESCENDING) \
            .limit(1) \
            .stream()

        should_create = True
        for quest_doc in existing_quests:
            last_created = quest_doc.to_dict().get("created_at")
            if last_created and (now - last_created.replace(tzinfo=pytz.UTC) < frequency):
                should_create = False
                break

        if should_create:
            quest_data = {
                "assigned_to": adopted_by or "",
                "created_at": now,
                "plant_id": plant_id,
                "proof_submission": {},
                "photo_url": None,
                "verified": False,
                "reward_points": 50,
                "status": "pending",
                "type": quest_type
            }
            quest_ref = quests_ref.document()
            quest_ref.set(quest_data)
            created_quests.append(quest_ref.id)

            # 🔄 Add quest ID to plant's "quests" field
            try:
                plants_ref.document(plant_id).update({
                    "quests": firestore.ArrayUnion([quest_ref.id])
                })
            except Exception as e:
                print(f"Error adding quest to plant {plant_id}: {e}")

            # 🔄 Add quest ID to user's "active_quests" field
            if adopted_by:
                try:
                    if quest_type == "Water Plant":
                        if last_watered:
                            watered_time = last_watered.replace(tzinfo=pytz.UTC)
                            if now - watered_time >= timedelta(days=1):
                                users_ref.document(adopted_by).update({
                                    "active_quests": firestore.ArrayUnion([quest_ref.id])
                                })
                    else:
                        users_ref.document(adopted_by).update({
                            "active_quests": firestore.ArrayUnion([quest_ref.id])
                        })
                except Exception as e:
                    print(f"Error updating active_quests for user {adopted_by}: {e}")

# return jsonify({
#     "status": "success",
#     "quests_created": len(created_quests),
#     "quest_ids": created_quests
# }), 200

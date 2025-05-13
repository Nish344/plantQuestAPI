from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from geopy.distance import geodesic
from datetime import datetime
import pytz

cred = credentials.Certificate("/workspaces/plantQuestAPI/plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")
initialize_app(cred)
db = firestore.client()
app = Flask(__name__)
timezone = pytz.timezone("Asia/Kolkata")

# 🔁 1. Update User Location
@app.route("/user/location", methods=["POST"])
def update_user_location():
    data = request.get_json()
    user_id = data.get("user_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if not all([user_id, lat, lng]):
        return jsonify({"error": "Missing user_id or location"}), 400

    db.collection("Users").document(user_id).update({
        "location": {"lat": lat, "lng": lng}
    })
    return jsonify({"message": "📍 Location updated successfully"})

# 🔍 2. Fetch Open Nearby Quests (within 500m)
@app.route("/quests/nearby", methods=["GET"])
def get_nearby_quests():
    user_id = request.args.get("user_id")
    user_doc = db.collection("Users").document(user_id).get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    user_loc = user_doc.to_dict().get("location")
    if not user_loc:
        return jsonify({"error": "User location not set"}), 400

    user_coords = (user_loc["lat"], user_loc["lng"])

    quests = []
    for plant_doc in db.collection("Plants").stream():
        plant = plant_doc.to_dict()
        plant_coords = (plant["location"]["lat"], plant["location"]["lng"])
        distance_m = geodesic(user_coords, plant_coords).meters
        if distance_m <= 500:
            # Fetch open quests for this plant
            nearby_quests = db.collection("Quests") \
                .where("plant_id", "==", plant_doc.id) \
                .where("status", "==", "pending") \
                .stream()
            for q in nearby_quests:
                quest = q.to_dict()
                quest["id"] = q.id
                quests.append(quest)

    return jsonify({"nearby_quests": quests})

# 🌱 3. Adopt Nearby Plant
@app.route("/user/adopt", methods=["POST"])
def adopt_plant():
    data = request.get_json()
    user_id = data.get("user_id")
    plant_id = data.get("plant_id")

    user_ref = db.collection("Users").document(user_id)
    plant_ref = db.collection("Plants").document(plant_id)

    user_doc = user_ref.get()
    plant_doc = plant_ref.get()
    if not (user_doc.exists and plant_doc.exists):
        return jsonify({"error": "Invalid user or plant ID"}), 404

    # Update plant's adopted_by field
    plant_ref.update({"adopted_by": user_id})
    # Add plant to user's adopted list
    user_ref.update({
        "adopted_plants": firestore.ArrayUnion([plant_id])
    })

    return jsonify({"message": f"🌿 Plant {plant_id} adopted by {user_id}!"})

# ✅ 4. View User Quests by Status
@app.route("/user/quests", methods=["GET"])
def view_user_quests():
    user_id = request.args.get("user_id")
    status = request.args.get("status", "pending")

    quests = db.collection("Quests") \
        .where("assigned_to", "==", user_id) \
        .where("status", "==", status) \
        .stream()

    return jsonify({
        "quests": [
            {**q.to_dict(), "id": q.id}
            for q in quests
        ]
    })

# 🧪 5. Dummy Quest Completion
@app.route("/user/complete_quest", methods=["POST"])
def complete_quest():
    data = request.get_json()
    quest_id = data.get("quest_id")
    user_id = data.get("user_id")

    quest_ref = db.collection("Quests").document(quest_id)
    quest_doc = quest_ref.get()

    if not quest_doc.exists:
        return jsonify({"error": "Quest not found"}), 404

    # Update quest
    quest_ref.update({
        "status": "completed",
        "proof_submission.timestamp": firestore.SERVER_TIMESTAMP,
        "proof_submission.verified": True
    })

    # Add quest to user's completed list and increment eco_points
    reward = quest_doc.to_dict().get("reward_points", 0)
    user_ref = db.collection("Users").document(user_id)
    user_ref.update({
        "quests_completed": firestore.ArrayUnion([quest_id]),
        "eco_points": firestore.Increment(reward)
    })

    return jsonify({"message": f"🎉 Quest {quest_id} marked as completed and {reward} points awarded!"})

@app.route("/")
def root():
    return "🌿 PlantQuest User API Ready!"

if __name__ == "__main__":
    app.run(debug=True)

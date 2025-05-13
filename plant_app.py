from flask import Flask, request, jsonify
import os
import uuid
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from kindwise import PlantApi
import datetime
from PIL import Image
import imagehash

app = Flask(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("./plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize KindWise Plant API
plant_api = PlantApi('lSVhhyMnVjzP6qmP4N0O0pUDvf7I16BOS3wY5Mww6vzpDSNiaf')

def encode_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def is_similar_image(new_image_path, existing_base64, threshold=5):
    new_hash = imagehash.average_hash(Image.open(new_image_path))
    existing_image_data = base64.b64decode(existing_base64)
    with open("temp_compare.jpg", "wb") as f:
        f.write(existing_image_data)
    existing_hash = imagehash.average_hash(Image.open("temp_compare.jpg"))
    os.remove("temp_compare.jpg")
    return abs(new_hash - existing_hash) <= threshold

def get_nearby_plants(lat, lng, radius_deg=0.00003):
    lower_lat = lat - radius_deg
    upper_lat = lat + radius_deg
    lower_lng = lng - radius_deg
    upper_lng = lng + radius_deg

    nearby = db.collection("Plants").where("location.lat", ">=", lower_lat).where("location.lat", "<=", upper_lat).stream()
    candidates = []
    for plant in nearby:
        data = plant.to_dict()
        if lower_lng <= data["location"]["lng"] <= upper_lng:
            candidates.append({"id": plant.id, **data})
    return candidates

def analyze_plant(image_path):
    try:
        result = {}
        identification = plant_api.identify(image_path, details=['url', 'common_names'])
        if not identification.result.is_plant.binary:
            return {"is_plant": False, "error": "Image does not appear to be a plant."}

        suggestions = [
            {
                "name": s.name,
                "probability": s.probability,
                "common_names": s.details.get("common_names", []),
                "url": s.details.get("url", "")
            }
            for s in identification.result.classification.suggestions
        ]

        health = plant_api.health_assessment(image_path, details=["description", "treatment"])
        is_healthy = health.result.is_healthy.binary
        health_score = 9.0 if is_healthy else 5.0

        diseases_raw = [
            {
                "name": d.name,
                "probability": d.probability,
                "description": d.details.get("description"),
                "treatment": d.details.get("treatment")
            }
            for d in health.result.disease.suggestions
        ]

        diseases = sorted(diseases_raw, key=lambda d: d.get("probability", 0), reverse=True)[:2]

        result["is_plant"] = True
        result["suggestions"] = suggestions
        result["health_status"] = "healthy" if is_healthy else "diseased"
        result["health_score"] = health_score
        result["diseases"] = diseases

        return result

    except Exception as e:
        return {"is_plant": False, "error": str(e)}

@app.route('/api/check-health', methods=['POST'])
def check_health():
    data = request.json
    image_path = data.get("image_path")

    if not image_path or not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Invalid image path"}), 400

    analysis = analyze_plant(image_path)
    if not analysis.get("is_plant", False):
        return jsonify({"success": False, "error": analysis.get("error", "Not a valid plant image")}), 400

    return jsonify({"success": True, "analysis": analysis})

@app.route('/api/register-plant', methods=['POST'])
def register_plant():
    data = request.json
    user_id = data.get("user_id")
    lat = float(data.get("lat"))
    lng = float(data.get("lng"))
    image_path = data.get("image_path")

    if not all([user_id, lat, lng, image_path]) or not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Missing or invalid fields"}), 400

    analysis = analyze_plant(image_path)
    if not analysis.get("is_plant", False):
        return jsonify({"success": False, "error": analysis.get("error")}), 400

    species = analysis["suggestions"][0]["name"] if analysis["suggestions"] else "Unknown"
    common_name = analysis["suggestions"][0].get("common_names", ["Unknown"])[0]
    health_score = analysis.get("health_score", 7.0)
    diseases = analysis.get("diseases", [])
    health_status = analysis.get("health_status", "unknown")

    nearby = get_nearby_plants(lat, lng)
    new_image_base64 = encode_image_base64(image_path)

    for existing in nearby:
        if existing.get("species", "").lower() == species.lower():
            if "image_base64" in existing and is_similar_image(image_path, existing["image_base64"]):
                return jsonify({
                    "success": False,
                    "error": f"Duplicate plant detected nearby (Species: {species})."
                }), 409

    plant_id = f"plant_{uuid.uuid4().hex[:8]}"
    db.collection("Plants").document(plant_id).set({
        "species": species,
        "common_name": common_name,
        "location": {"lat": lat, "lng": lng},
        "health_score": health_score,
        "health_status": health_status,
        "last_watered": None,
        "adopted_by": None,
        "quests": [],
        "added_by": user_id,
        "image_base64": new_image_base64,
        "registered_date": firestore.SERVER_TIMESTAMP,
        "diseases": diseases
    })

    db.collection("Users").document(user_id).update({
        "added_plants": firestore.ArrayUnion([plant_id]),
        "eco_points": firestore.Increment(100)
    })

    photo_id = f"photo_{uuid.uuid4().hex[:8]}"
    db.collection("Photos").document(photo_id).set({
        "user_id": user_id,
        "plant_id": plant_id,
        "image_url": image_path,
        "ai_analysis": {
            "species": species,
            "health_status": health_status,
            "diseases": diseases
        },
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    return jsonify({
        "success": True,
        "plant_id": plant_id,
        "message": f"Plant {species} ({common_name}) successfully registered.",
        "eco_points_earned": 100,
        "analysis": analysis
    }), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

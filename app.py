from flask import Flask, request, jsonify
import requests
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# 🔐 Initialize Firebase
cred = credentials.Certificate("firebase_key.json")  # <-- Replace with your path
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🌿 PlantNet API
PLANTNET_API_KEY = "2b106qi81SCWarr0sxqfOpIb2"
PLANTNET_PROJECT = "all"
PLANTNET_URL = f"https://my-api.plantnet.org/v2/identify/{PLANTNET_PROJECT}?api-key={PLANTNET_API_KEY}"

# 📌 Register Plant
@app.route('/register_plant', methods=['POST'])
def register_plant():
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lng = request.form.get('longitude')

    if not image or not lat or not lng:
        return jsonify({"error": "Image and location are required"}), 400

    files = [('images', (image.filename, image, 'image/jpeg'))]
    data = {'organs': ['flower']}

    try:
        response = requests.post(PLANTNET_URL, files=files, data=data)
        response.raise_for_status()
        result = response.json()

        if not result.get('results'):
            return jsonify({"error": "No plant identified"}), 404

        species = result['results'][0].get('species', {})
        doc = {
            "scientific_name": species.get('scientificName', 'Unknown'),
            "common_names": species.get('commonNames', []),
            "genus": species.get('genus', {}).get('scientificName', 'Unknown'),
            "family": species.get('family', {}).get('scientificName', 'Unknown'),
            "score": result['results'][0].get('score', 0.0),
            "location": {"lat": float(lat), "lng": float(lng)},
            "last_watered": None,
            "last_health_check": None,
            "quests": [],
            "timestamp": datetime.datetime.utcnow()
        }

        doc_ref = db.collection("plants").add(doc)
        return jsonify({"message": "Plant registered", "plant_id": doc_ref[1].id, "data": doc}), 200

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# 💧 Water Plant
@app.route('/water_plant', methods=['POST'])
def water_plant():
    data = request.json
    plant_id = data.get('plant_id')

    if not plant_id:
        return jsonify({"error": "plant_id is required"}), 400

    db.collection("plants").document(plant_id).update({
        "last_watered": datetime.datetime.utcnow()
    })

    return jsonify({"message": "Watered plant"}), 200

# 🧪 Health Check Update
@app.route('/health_check', methods=['POST'])
def health_check():
    data = request.json
    plant_id = data.get('plant_id')
    health_note = data.get('note', '')

    if not plant_id:
        return jsonify({"error": "plant_id is required"}), 400

    db.collection("plants").document(plant_id).update({
        "last_health_check": datetime.datetime.utcnow(),
        "health_note": health_note
    })

    return jsonify({"message": "Health check updated"}), 200

# 🎯 Generate Sample Quests
@app.route('/generate_quests', methods=['POST'])
def generate_quests():
    data = request.json
    plant_id = data.get('plant_id')

    if not plant_id:
        return jsonify({"error": "plant_id is required"}), 400

    quests = [
        {"type": "Watering", "points": 10},
        {"type": "Photo Upload", "points": 15},
        {"type": "Clean Area", "points": 20}
    ]

    db.collection("plants").document(plant_id).update({
        "quests": quests
    })

    return jsonify({"message": "Quests generated", "quests": quests}), 200

# 🌿 View Plant Info
@app.route('/plant/<plant_id>', methods=['GET'])
def get_plant(plant_id):
    doc = db.collection("plants").document(plant_id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({"error": "Plant not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

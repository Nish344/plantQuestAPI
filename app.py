from flask import Flask, request, jsonify
import requests
import json
import datetime
import os
import uuid

app = Flask(__name__)

PLANTNET_API_KEY = "2b106qi81SCWarr0sxqfOpIb2"
PLANTNET_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"
DATA_FILE = "plants.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)

# ✅ Register a plant
@app.route('/register_plant', methods=['POST'])
def register_plant():
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lng = request.form.get('longitude')

    if not image or not lat or not lng:
        return jsonify({"error": "Missing data"}), 400

    files = [('images', (image.filename, image, 'image/jpeg'))]
    data = {'organs': ['flower']}

    try:
        response = requests.post(PLANTNET_URL, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        if not result.get('results'):
            return jsonify({"error": "No plant identified"}), 404

        species = result['results'][0].get('species', {})
        plant_id = str(uuid.uuid4())

        plant = {
            "plant_id": plant_id,
            "scientific_name": species.get('scientificName', 'Unknown'),
            "common_names": species.get('commonNames', []),
            "genus": species.get('genus', {}).get('scientificName', 'Unknown'),
            "family": species.get('family', {}).get('scientificName', 'Unknown'),
            "score": result['results'][0].get('score', 0.0),
            "location": {"lat": float(lat), "lng": float(lng)},
            "last_watered": None,
            "last_health_check": None,
            "health_note": "",
            "quests": [],
            "timestamp": str(datetime.datetime.utcnow())
        }

        data = load_data()
        data.append(plant)
        save_data(data)

        return jsonify({"message": "Plant registered", "plant_id": plant_id, "data": plant}), 200

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# 💧 Water a plant
@app.route('/water_plant', methods=['POST'])
def water_plant():
    plant_id = request.json.get('plant_id')
    data = load_data()

    for plant in data:
        if plant['plant_id'] == plant_id:
            plant['last_watered'] = str(datetime.datetime.utcnow())
            save_data(data)
            return jsonify({"message": "Plant watered"}), 200

    return jsonify({"error": "Plant not found"}), 404

# 🧪 Health check update
@app.route('/health_check', methods=['POST'])
def health_check():
    req = request.json
    plant_id = req.get('plant_id')
    note = req.get('note', '')

    data = load_data()
    for plant in data:
        if plant['plant_id'] == plant_id:
            plant['last_health_check'] = str(datetime.datetime.utcnow())
            plant['health_note'] = note
            save_data(data)
            return jsonify({"message": "Health check updated"}), 200

    return jsonify({"error": "Plant not found"}), 404

# 🎯 Generate demo quests
@app.route('/generate_quests', methods=['POST'])
def generate_quests():
    plant_id = request.json.get('plant_id')
    quests = [
        {"type": "Watering", "points": 10},
        {"type": "Photo Upload", "points": 15},
        {"type": "Clean Area", "points": 20}
    ]

    data = load_data()
    for plant in data:
        if plant['plant_id'] == plant_id:
            plant['quests'] = quests
            save_data(data)
            return jsonify({"message": "Quests assigned", "quests": quests}), 200

    return jsonify({"error": "Plant not found"}), 404

# 🔍 Get plant info
@app.route('/plant/<plant_id>', methods=['GET'])
def get_plant(plant_id):
    data = load_data()
    for plant in data:
        if plant['plant_id'] == plant_id:
            return jsonify(plant), 200
    return jsonify({"error": "Plant not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

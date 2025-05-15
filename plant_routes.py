from flask import Blueprint, request, jsonify
import os
import uuid
import base64
from firebase_admin import firestore
from kindwise import PlantApi
import pytz
from datetime import timedelta, datetime
from PIL import Image
import imagehash
from io import BytesIO
import base64

plant_routes = Blueprint("plant_routes", __name__)
db = firestore.client()
plant_api = PlantApi('Kindwise-API-KEY')




def compress_and_encode_image(base64_string, max_size=(512, 512), quality=70):
    # Decode base64 to image
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))

    # Convert to RGB to avoid mode errors (e.g., from PNG)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize image (maintain aspect ratio)
    image.thumbnail(max_size)

    # Save to BytesIO with reduced quality
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    compressed_bytes = buffer.getvalue()

    # Encode to base64 again
    return base64.b64encode(compressed_bytes).decode("utf-8")



def encode_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def is_similar_image(image_path, existing_base64, threshold=5):
    new_hash = imagehash.average_hash(Image.open(image_path))
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


@plant_routes.route('/generate_quests', methods=['POST'])
def generate_quests():
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

                
                try:
                    plants_ref.document(plant_id).update({
                        "quests": firestore.ArrayUnion([quest_ref.id])
                    })
                except Exception as e:
                    print(f"Error adding quest to plant {plant_id}: {e}")

                
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

    return jsonify({
        "status": "success",
        "quests_created": len(created_quests),
        "quest_ids": created_quests
    }), 200

@plant_routes.route('/api/check-health', methods=['POST'])
def check_health():
    data = request.json
    image_path = data.get("image_path")

    if not image_path or not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Invalid image path"}), 400

    analysis = analyze_plant(image_path)
    if not analysis.get("is_plant", False):
        return jsonify({"success": False, "error": analysis.get("error", "Not a valid plant image")}), 400

    return jsonify({"success": True, "analysis": analysis})


@plant_routes.route('/api/register-plant', methods=['POST'])
def register_plant():
    data = request.json
    user_id = data.get("user_id")
    lat = float(data.get("lat"))
    lng = float(data.get("lng"))
    original_base64 = data.get("image_base64")
    if not original_base64:
        return jsonify({"success": False, "error": "Image missing"}), 400

    # Compress image to reduce Firestore size usage
    image_base64 = compress_and_encode_image(original_base64)

    if not all([user_id, lat, lng, image_base64]):
        return jsonify({"success": False, "error": "Missing or invalid fields"}), 400

    # Save base64 image temporarily for processing
    temp_image_path = "temp_uploaded.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    analysis = analyze_plant(temp_image_path)
    if not analysis.get("is_plant", False):
        os.remove(temp_image_path)
        return jsonify({"success": False, "error": analysis.get("error")}), 400

    species = analysis["suggestions"][0]["name"] if analysis["suggestions"] else "Unknown"
    common_name = analysis["suggestions"][0].get("common_names", ["Unknown"])[0]
    health_score = analysis.get("health_score", 7.0)
    diseases = analysis.get("diseases", [])
    health_status = analysis.get("health_status", "unknown")

    nearby = get_nearby_plants(lat, lng)

    for existing in nearby:
        if existing.get("species", "").lower() == species.lower():
            if "image_base64" in existing and is_similar_image(image_base64, existing["image_base64"]):
                os.remove(temp_image_path)
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
        "image_base64": image_base64,
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
        "image_url": None,  # You can store a URL if image is uploaded to cloud
        "ai_analysis": {
            "species": species,
            "health_status": health_status,
            "diseases": diseases
        },
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    os.remove(temp_image_path)

    return jsonify({
        "success": True,
        "plant_id": plant_id,
        "message": f"Plant {species} ({common_name}) successfully registered.",
        "eco_points_earned": 100,
        "analysis": analysis
    }), 201


@plant_routes.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

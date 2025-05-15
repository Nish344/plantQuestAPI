import requests
import json
import pprint

API_URL = "http://localhost:5000/api/register-plant"

user_id = "uid123"
lat = 122.9716
lng = 10.5946

img_paths = ["img1.jpg", "img2.jpg"]

def register_plant(image_path):
    payload = {
        "user_id": user_id,
        "lat": lat,
        "lng": lng,
        "image_path": image_path
    }

    try:
        response = requests.post(API_URL, json=payload)
        response_data = response.json()

        if response.status_code == 201:
            analysis = response_data.get("analysis", {})
            suggestions = analysis.get("suggestions", [{}])
            species = suggestions[0].get("name", "Unknown")
            common_name = suggestions[0].get("common_names", ["Unknown"])[0]
            health_status = analysis.get("health_status", "unknown").capitalize()
            health_score = analysis.get("health_score", "N/A")
            diseases = analysis.get("diseases", [])
            for disease in diseases:
                treatment = disease.get("treatment", {})
                if "biological" in treatment and isinstance(treatment["biological"], list):
                    treatment["biological"] = treatment["biological"][:3]

            print(f"\n===== {health_status} Plant Response =====")
            print(f"Message        : {response_data['message']}")
            print(f"Species        : {species} ({common_name})")
            print(f"Health Score   : {health_score}")
            print(f"Diseases       : {json.dumps(diseases, indent=4)}")
            print(f" Image Path     : {image_path}")
            print(f"Plant ID       : {response_data.get('plant_id')}")

        else:
            error = response_data.get("error", "Unknown error")
            print(f"\n===== Failed Plant Registration =====")
            print(f"Error {response.status_code}: {error}")
            print(f"Image Path: {image_path}")

    except Exception as e:
        print(f"\n===== Exception During Request =====")
        print(f"Exception occurred: {e}")
        print(f"Image Path: {image_path}")

if __name__ == "__main__":
    for path in img_paths:
        register_plant(path)

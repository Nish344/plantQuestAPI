import requests
import json

# Replace this with your local or deployed server URL
BASE_URL = "http://localhost:5000"

# Sample test image path (this should exist locally)
TEST_IMAGE_PATH = "/workspaces/plantQuestAPI/Uploads/neem.jpeg"  # Change to your actual image path

# Uploading the image to simulate and send image_path to API
def simulate_upload(image_path):
    # Save image locally or simulate a public URL if deployed elsewhere
    return image_path

# 1. Test /api/check-health endpoint
def test_check_health():
    image_path = simulate_upload(TEST_IMAGE_PATH)
    payload = {"image_path": image_path}
    response = requests.post(f"{BASE_URL}/api/check-health", json=payload)
    
    print("\n[TEST] /api/check-health")
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))


# 2. Test /api/register-plant endpoint
def test_register_plant():
    image_path = simulate_upload(TEST_IMAGE_PATH)
    payload = {
        "user_id": "uid123",
        "lat": 26.8467,
        "lng": 80.9462,
        "image_path": image_path
    }
    response = requests.post(f"{BASE_URL}/api/register-plant", json=payload)

    print("\n[TEST] /api/register-plant")
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))


# Run tests
if __name__ == "__main__":
    test_check_health()
    test_register_plant()

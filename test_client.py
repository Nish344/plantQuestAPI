import requests

BASE = "http://127.0.0.1:5000"

# ✅ 1. Register Plant
def test_register_plant():
    with open("test_image.jpeg", "rb") as img:
        data = {
            "latitude": "28.6139",
            "longitude": "77.2090"
        }
        files = {
            "image": ("test_image.jpeg", img, "image/jpeg")
        }
        res = requests.post(f"{BASE}/register_plant", files=files, data=data)
        print(res.json())
        return res.json().get("plant_id")

# ✅ 2. Water Plant
def test_water_plant(plant_id):
    res = requests.post(f"{BASE}/water_plant", json={"plant_id": plant_id})
    print(res.json())

# ✅ 3. Health Check
def test_health_check(plant_id):
    res = requests.post(f"{BASE}/health_check", json={"plant_id": plant_id, "note": "Looks healthy!"})
    print(res.json())

# ✅ 4. Generate Quests
def test_generate_quests(plant_id):
    res = requests.post(f"{BASE}/generate_quests", json={"plant_id": plant_id})
    print(res.json())

# ✅ 5. View Plant Info
def test_view(plant_id):
    res = requests.get(f"{BASE}/plant/{plant_id}")
    print(res.json())

# Run All Tests
if __name__ == "__main__":
    pid = test_register_plant()
    if pid:
        test_water_plant(pid)
        test_health_check(pid)
        test_generate_quests(pid)
        test_view(pid)

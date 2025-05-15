```
# 🌱 PlantQuest API

A Flask-based backend for gamified plant adoption, health monitoring, and care using AI and Firebase. The system allows users to adopt plants, complete quests (e.g., watering, assessment), and chat with their plants using a Gemini-powered persona chatbot.

---

## 🚀 Features

- 🔍 **AI Plant Analysis** – Identify species, assess health, and detect diseases via KindWise API.
- 📍 **Location-Aware Registration** – Prevent duplicate plant registration nearby.
- 🎯 **Recurring Quests** – Auto-generates quests like watering, health check, photo update.
- 💬 **Plant Persona Chatbot** – Chat with your plant using Google Gemini (LLM) with contextual memory.
- 🌐 **Firebase Firestore Integration** – Stores users, plants, photos, and quest data.
- 🎉 **Gamification** – Earn eco-points for actions like adding or caring for plants.

---

## 🧩 Tech Stack

- **Python + Flask** – Backend API
- **Firebase Firestore** – NoSQL DB
- **KindWise API** – Plant analysis
- **Google Gemini API** – Chatbot
- **Pillow + ImageHash** – Image comparison
- **UUID + Base64** – Unique ID & image encoding

---

## 📁 Project Structure

```

plantquest-api/
│
├── app.py                        # Flask app setup
├── plant\_routes.py              # Plant logic (register, health check, quests)
├── user\_routes.py               # User-related endpoints (not shown here)
├── chatbot.py                   # Gemini chatbot logic
├── requirements.txt             # Python dependencies
├── README.md                    # You're here 🌿
└── plantquest-\*.json            # Firebase Admin SDK credentials

````

---

## 🛠️ Setup Instructions

### 1. 📦 Install Dependencies

```bash
pip install -r requirements.txt
````

> Make sure you have Python 3.8+ installed.

---

### 2. 🔑 Setup Firebase Admin SDK

* Download the Firebase Admin SDK JSON file.
* Rename it if needed and place it in the root directory.
* Update the path in `app.py` and `chatbot.py`:

```python
credentials.Certificate("plantquest-...json")
```

---

### 3. 🔐 Add API Keys

* **KindWise API Key** (used in `plant_routes.py`)
* **Gemini API Key** (used in `chatbot.py`)

Update:

```python
# plant_routes.py
plant_api = PlantApi('YOUR_KINDWISE_API_KEY')

# chatbot.py
genai.configure(api_key='YOUR_GEMINI_API_KEY')
```

---

## 🌐 API Endpoints

### ✅ Health Check

```http
GET /api/health
```

---

### 🌿 Register Plant

```http
POST /api/register-plant
Content-Type: application/json

{
  "user_id": "user_123",
  "lat": 12.9716,
  "lng": 77.5946,
  "image_path": "./images/leaf.jpg"
}
```

---

### 🧪 Check Plant Health

```http
POST /api/check-health
Content-Type: application/json

{
  "image_path": "./images/leaf.jpg"
}
```

---

### 🧾 Generate Daily Quests

```http
POST /generate_quests
```

Creates new quests (e.g., watering, photo, health check) based on rules and frequency.

---

## 🤖 Chat with a Plant (Gemini LLM)

Inside `chatbot.py`:

```python
plant_id = "plant_b2eb9419"
reply = plant_chatbot(plant_id, "How are you feeling today?")
print("🌿 Plant says:", reply)
```

You can also create a frontend to call this with a chat interface.

---

## 🧪 Testing Locally

```bash
python app.py
```

App runs on: `http://0.0.0.0:5000`

---

## ✅ Future Improvements

* Add user authentication via Firebase Auth
* Expand chatbot with memory and multi-turn context
* Add weather-based reminders and local recommendations
* Push notification support

---

## 🧑‍💻 Authors

**Nishanth Antony**
**Prajwal S**
**Nikhil R**
**Aryan Mishra**

---

## 📄 License

MIT License – feel free to fork, extend, and plant something amazing 🌼

```



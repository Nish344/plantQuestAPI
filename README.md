# PlantQuest API

PlantQuest API is a comprehensive Flask-based backend service for plant identification, health assessment, user-driven plant registration, location tracking, quest management, and plant adoption. It integrates the KindWise Plant API for AI-powered plant analysis and uses Firebase Firestore as the real-time database backend.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [Plant Identification & Health](#plant-identification--health)
  - [Plant Registration](#plant-registration)
  - [User Location & Quests](#user-location--quests)
- [How It Works](#how-it-works)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

### Plant Analysis & Registration

- **Plant Health Check**: Identify plants and analyze their health status and diseases using AI.
- **Plant Registration**: Register new plants with geolocation and user info.
- **Duplicate Detection**: Prevent duplicate plant registrations nearby using image similarity.
- **Eco Points**: Reward users with eco points for adding plants.

### User Location & Quest Management

- **Update User Location**: Users can update their current GPS coordinates.
- **Fetch Nearby Quests**: Retrieve open quests within 500 meters of the user.
- **Adopt Plants**: Users can adopt plants nearby.
- **View User Quests**: Filter quests by status (pending, completed).
- **Complete Quests**: Mark quests as completed and earn eco points.

---

## Technologies Used

- **Python 3**
- **Flask** - Web framework for REST API
- **KindWise Plant API** - AI for plant identification and health assessment
- **Firebase Admin SDK** - Firestore database integration
- **Pillow & ImageHash** - Image processing and similarity detection
- **Geopy** - Geographic distance calculations
- **UUID & Base64** - Unique IDs and image encoding
- **pytz** - Timezone management

---

## Setup and Installation

### Prerequisites

- Python 3.7+
- Firebase project with Firestore enabled
- KindWise Plant API key
- Required Python packages

### Clone the repository

```bash
git clone 
cd 
```

### Install dependencies

```bash
pip install -r requirements.txt
```

Ensure `requirements.txt` includes:

```
Flask
firebase-admin
kindwise
Pillow
imagehash
geopy
pytz
```

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/).
2. Enable Firestore database.
3. Generate a service account key JSON file from Project Settings > Service Accounts.
4. Save the JSON file locally (e.g., `/path/to/firebase-adminsdk.json`).
5. Update Firebase initialization paths in your Flask app code:

```python
cred = credentials.Certificate("/path/to/firebase-adminsdk.json")
initialize_app(cred)
```

### KindWise Plant API Setup

Obtain your API key from KindWise and update the initialization:

```python
plant_api = PlantApi('')
```

### Running the Application

Run the Flask app with:

```bash
python app.py
```

The API will be accessible at `http://0.0.0.0:5000`.

---

## Configuration

- **Firebase credentials path**: Update `credentials.Certificate()` path in both parts of the code.
- **KindWise API key**: Replace the placeholder with your actual API key.
- **Image paths**: Ensure the server can access the image paths provided in requests.
- **Timezone**: Default set to Asia/Kolkata; adjust if needed.

---

## API Endpoints

### Plant Identification & Health

#### POST `/api/check-health`

Analyze a plant image for health status.

**Request JSON:**

```json
{
  "image_path": "/path/to/plant_image.jpg"
}
```

**Response:**

- Success (200):

```json
{
  "success": true,
  "analysis": {
    "is_plant": true,
    "suggestions": [...],
    "health_status": "healthy",
    "health_score": 9.0,
    "diseases": [...]
  }
}
```

- Failure (400):

```json
{
  "success": false,
  "error": "Invalid image path"
}
```

or

```json
{
  "success": false,
  "error": "Image does not appear to be a plant."
}
```

---

### Plant Registration

#### POST `/api/register-plant`

Register a new plant with user info, location, and image.

**Request JSON:**

```json
{
  "user_id": "user123",
  "lat": 12.345678,
  "lng": 98.765432,
  "image_path": "/path/to/plant_image.jpg"
}
```

**Response:**

- Success (201):

```json
{
  "success": true,
  "plant_id": "plant_abc12345",
  "message": "Plant  () successfully registered.",
  "eco_points_earned": 100,
  "analysis": {...}
}
```

- Failure (400 or 409):

```json
{
  "success": false,
  "error": "Duplicate plant detected nearby (Species: )."
}
```

or

```json
{
  "success": false,
  "error": "Missing or invalid fields"
}
```

---

### User Location & Quests

#### POST `/user/location`

Update user GPS location.

**Request JSON:**

```json
{
  "user_id": "user123",
  "lat": 12.345678,
  "lng": 98.765432
}
```

**Response:**

```json
{
  "message": "📍 Location updated successfully"
}
```

---

#### GET `/quests/nearby`

Fetch open quests within 500 meters of the user.

**Query Parameters:**

- `user_id` (required)

**Response:**

```json
{
  "nearby_quests": [
    {
      "id": "quest123",
      "plant_id": "plant456",
      "status": "pending",
      ...
    },
    ...
  ]
}
```

---

#### POST `/user/adopt`

Adopt a nearby plant.

**Request JSON:**

```json
{
  "user_id": "user123",
  "plant_id": "plant456"
}
```

**Response:**

```json
{
  "message": "🌿 Plant plant456 adopted by user123!"
}
```

---

#### GET `/user/quests`

View user quests filtered by status.

**Query Parameters:**

- `user_id` (required)
- `status` (optional, default: `pending`)

**Response:**

```json
{
  "quests": [
    {
      "id": "quest123",
      "assigned_to": "user123",
      "status": "pending",
      ...
    },
    ...
  ]
}
```

---

#### POST `/user/complete_quest`

Mark a quest as completed and reward eco points.

**Request JSON:**

```json
{
  "user_id": "user123",
  "quest_id": "quest123"
}
```

**Response:**

```json
{
  "message": "🎉 Quest quest123 marked as completed and 50 points awarded!"
}
```

---

### Health Check

#### GET `/api/health`

Check API service status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-05-13T13:31:00.000000"
}
```

---

## How It Works

- **Plant Analysis**: Uses KindWise API to identify and analyze plant health from images.
- **Duplicate Detection**: Uses perceptual image hashing to avoid registering duplicate plants in close proximity.
- **Location-Based Quests**: Users can receive quests related to plants near their current location.
- **Adoption & Rewards**: Users can adopt plants and complete quests to earn eco points.
- **Real-Time Updates**: Firebase Firestore stores and syncs user, plant, quest, and photo data.

---

## Notes

- Image files must be accessible to the Flask server.
- Geolocation radius for quests is 500 meters.
- Image similarity threshold is set to 5 (average hash difference).
- Firebase Firestore security rules should be configured to allow appropriate read/write operations.
- Timezone is set to Asia/Kolkata by default.

---

## Author
**Nishanth Antony**

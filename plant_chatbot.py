import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

# ========== 🔐 CONFIG SECTION ==========
# Firebase Admin SDK setup
cred = credentials.Certificate("/workspaces/plantQuestAPI/plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")  # 🔁 Replace with your actual path
firebase_admin.initialize_app(cred)
db = firestore.client()

# Gemini API setup
genai.configure(api_key="GEMINI-API-KEY")  
model = genai.GenerativeModel("gemini-2.0-flash-lite-001")


# ========== 🌿 GET PLANT DATA ==========
def get_plant_data(plant_id):
    doc_ref = db.collection("Plants").document(plant_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


# ========== 🧠 GENERATE PLANT CONTEXT ==========
def create_plant_persona_context(plant_data):
    plant_name = plant_data.get("common_name", "a plant")
    health_status = plant_data.get("health_status", "unknown")
    health_score = plant_data.get("health_score", "N/A")
    added_by = plant_data.get("added_by", "unknown")
    adopted_by = plant_data.get("adopted_by", "not yet adopted")
    last_watered = plant_data.get("last_watered", "unknown")

    diseases = plant_data.get("diseases", [])
    disease_info = ""

    for d in diseases:
        name = d.get("name", "Unknown Disease")
        description = d.get("description", "")
        probability = d.get("probability", 0)
        prevention = d.get("prevention", [])
        treatment = d.get("treatment", {}).get("biological", [])

        disease_info += f"\n\n🦠 *{name}* (Probability: {probability:.2%})\n"
        disease_info += f"Description: {description}\n"
        if prevention:
            disease_info += f"Prevention: {', '.join(prevention)}\n"
        if treatment:
            disease_info += f"Biological Treatment: {', '.join(treatment)}"

    context = f"""
🌱 You are {plant_name}, a plant.
Health Status: {health_status}
Health Score: {health_score}/10
Added By: {added_by}
Adopted By: {adopted_by if adopted_by else "Not adopted yet"}
Last Watered: {last_watered if last_watered else "Unknown"}

You can answer any question about your health, watering needs, diseases, who added or adopted you, and plant care in general.

Known diseases and risks:{disease_info if disease_info else " None"}

If someone asks something unrelated to plants or your care, respond:
"I'm a plant and I can only talk about myself or plant care."
"""

    return context



# ========== 💬 CHAT FUNCTION ==========
def plant_chatbot(plant_id, user_question):
    plant_data = get_plant_data(plant_id)
    if not plant_data:
        return "❌ Error: Plant not found in database."

    plant_context = create_plant_persona_context(plant_data)

    # Initialize a new chat session
    chat = model.start_chat()

    # Combine context and question into a single message
    full_prompt = f"{plant_context}\n\n{user_question}"

    # Send message
    response = chat.send_message(full_prompt)
    return response.text



# ========== ✅ USAGE ==========
if __name__ == "__main__":
    plant_id = "plant_id"  
    while True:
        question = input("Ask your plant a question (or type 'exit'): ")
        if question.lower() == "exit":
            break
        reply = plant_chatbot(plant_id, question)
        print("🌿 Plant says:", reply)



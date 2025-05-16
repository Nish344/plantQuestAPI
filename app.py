from flask import Flask
from firebase_admin import credentials, initialize_app
import firebase_admin
from dotenv import load_dotenv

load_dotenv()

# Firebase initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("./plantquest-8a4bd-firebase-adminsdk-fbsvc-ffc04c7186.json")
    initialize_app(cred)


from plant_routes import plant_routes
from user_routes import user_bp

app = Flask(__name__)


# Register blueprint
app.register_blueprint(plant_routes)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

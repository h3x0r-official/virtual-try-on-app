# backend/app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
CORS(app)

# --- Database Configuration ---
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("No DATABASE_URL set for Flask application")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable modification tracking
db = SQLAlchemy(app) # Initialize SQLAlchemy with the app
# -----------------------------

# --- Database Models ---
class ClothingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    imageUrl = db.Column(db.String(255), nullable=True) # Assuming URL or path

    def __repr__(self):
        return f'<ClothingItem {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "imageUrl": self.imageUrl
        }
# ----------------------

# Dummy data (keep for now, maybe for seeding later)
# dummy_catalog = [...] # You can remove or comment this out later

@app.route("/api/hello")
def hello_world():
    return jsonify(message="Hello from Flask Backend!")

@app.route("/api/catalog")
def get_catalog():
    try:
        items = ClothingItem.query.all()
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        # Log the error e
        print(f"Error fetching catalog: {e}")
        return jsonify({"error": "Could not fetch catalog"}), 500


# --- Database Initialization Command (Optional but Recommended) ---
# You can run this once from the Flask shell to create tables
# In your terminal (with venv activated):
# > flask shell
# >>> from app import db
# >>> db.create_all()
# >>> exit()
# -----------------------------------------------------------------

# Add other routes later...

# if __name__ == '__main__':
#    app.run(debug=True) # Keep debug=True for development
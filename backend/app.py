# backend/app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS # Import CORS

load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes on this app

# Dummy clothing data
dummy_catalog = [
    {"id": 1, "name": "Classic Blue Kurta", "price": 2500, "imageUrl": "/images/kurta1.jpg"},
    {"id": 2, "name": "Embroidered Lawn Kameez", "price": 3200, "imageUrl": "/images/kameez1.jpg"},
    {"id": 3, "name": "Printed Cotton Shirt", "price": 1800, "imageUrl": "/images/shirt1.jpg"},
]

@app.route("/api/hello")
def hello_world():
    return jsonify(message="Hello from Flask Backend!")

@app.route("/api/catalog")
def get_catalog():
    # Later, fetch this from the database
    return jsonify(dummy_catalog)

# Add other routes later...

# if __name__ == '__main__':
#    app.run(debug=True)
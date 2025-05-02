# backend/app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

@app.route("/api/hello")
def hello_world():
    return jsonify(message="Hello from Flask Backend!")

# Add other routes for catalog, tryon etc. later

# Optional: Only run the server if the script is executed directly
# (Good practice, useful for configuration later)
# if __name__ == '__main__':
#    app.run(debug=True) # debug=True only for development!
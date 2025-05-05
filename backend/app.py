# backend/app.py
import os
from flask import Flask, jsonify, request # Import request
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from werkzeug.utils import secure_filename # Import secure_filename
from sqlalchemy import distinct # Import distinct

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Define the upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Configuration
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
    # Add the new brand column
    brand = db.Column(db.String(50), nullable=True, index=True) # Allow null initially, add index for filtering

    def __repr__(self):
        # Optionally include brand in representation
        return f'<ClothingItem {self.id}: {self.name} ({self.brand or "No Brand"})>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "imageUrl": self.imageUrl,
            "brand": self.brand # Include brand in the JSON output
        }
# ----------------------

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ---------------------

# Dummy data (keep for now, maybe for seeding later)
# dummy_catalog = [...] # You can remove or comment this out later

# --- Routes ---

# GET /api/hello - Health check endpoint
@app.route("/api/hello")
def hello_world():
    return jsonify(message="Hello from Flask Backend!")

# --- NEW BRANDS ENDPOINT ---
# GET /api/brands - Retrieve a unique, sorted list of brands
@app.route('/api/brands')
def get_brands():
    """
    Retrieves a unique list of non-null brand names from the clothing items,
    sorted alphabetically.
    """
    try:
        # Query for distinct, non-null brand names, ordered alphabetically
        brands_query = db.session.query(distinct(ClothingItem.brand))\
            .filter(ClothingItem.brand.isnot(None))\
            .order_by(ClothingItem.brand)\
            .all()
        # The query returns a list of tuples, e.g., [('BrandA',), ('BrandB',)]
        # Extract the first element from each tuple
        brands_list = [brand[0] for brand in brands_query]
        return jsonify(brands_list)
    except Exception as e:
        print(f"Error fetching brands: {e}")
        return jsonify({"error": "Could not fetch brands"}), 500
# -------------------------

# --- UPDATED CATALOG ENDPOINT ---
# GET /api/catalog - Retrieve clothing items (optionally filtered by brand)
@app.route("/api/catalog")
def get_catalog():
    """
    Retrieves clothing items. Accepts an optional 'brand' query parameter
    to filter results. If no 'brand' is provided, returns all items.
    """
    try:
        # Get the brand filter from query parameters, if provided
        brand_filter = request.args.get('brand')

        # Start building the query
        query = ClothingItem.query

        # Apply filter if brand_filter exists
        if (brand_filter):
            # Use filter_by for simple equality checks
            query = query.filter_by(brand=brand_filter)
            print(f"Filtering catalog for brand: {brand_filter}") # Log filtering

        # Execute the final query (either filtered or unfiltered)
        items = query.all()

        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        print(f"Error fetching catalog: {e}")
        return jsonify({"error": "Could not fetch catalog"}), 500
# -----------------------------

# --- NEW UPLOAD ROUTE ---
@app.route('/api/upload', methods=['POST'])
def upload_user_image():
    if 'user_image' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['user_image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename) # Sanitize filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            print(f"File saved successfully: {save_path}") # Log success
            # In a real app, you might save the filename/path to the DB
            # or return a unique identifier/URL (especially if using S3 later)
            return jsonify({
                "message": f"File '{filename}' uploaded successfully.",
                "filename": filename # Return the saved filename
                }), 200
        except Exception as e:
            print(f"Error saving file: {e}") # Log the exception
            return jsonify({"error": "Failed to save file on server"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400
# ------------------------

# --- NEW TRY-ON ENDPOINT ---
@app.route('/api/tryon', methods=['POST'])
def process_tryon():
    """
    (Simulated) Processes a virtual try-on request.
    Expects JSON body with 'userImageFilename' and 'clothingItemId'.
    Returns a simulated result image URL.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_image_filename = data.get('userImageFilename')
    clothing_item_id = data.get('clothingItemId')

    if not user_image_filename or not clothing_item_id:
        return jsonify({"error": "Missing 'userImageFilename' or 'clothingItemId' in request body"}), 400

    try:
        # 1. Validate user image file existence
        user_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(user_image_filename))
        if not os.path.exists(user_image_path):
            print(f"Try-on Error: User image not found at {user_image_path}")
            return jsonify({"error": f"User image '{user_image_filename}' not found on server"}), 404

        # 2. Validate clothing item existence
        clothing_item = ClothingItem.query.get(clothing_item_id)
        if not clothing_item:
            print(f"Try-on Error: Clothing item ID {clothing_item_id} not found")
            return jsonify({"error": f"Clothing item with ID {clothing_item_id} not found"}), 404

        # --- SIMULATED TRY-ON PROCESSING ---
        print("-" * 20)
        print(f"Simulating Try-On:")
        print(f"  User Image: {user_image_path}")
        print(f"  Clothing Item: ID={clothing_item.id}, Name='{clothing_item.name}', Image='{clothing_item.imageUrl}'")
        # In a real application, this is where you would call your
        # image processing library/service (e.g., OpenCV, a dedicated ML model API)
        # using user_image_path and clothing_item.imageUrl (or other relevant data).
        # The result would be a new image file/URL.

        # For now, just return the original clothing item's URL as the "result"
        simulated_result_url = clothing_item.imageUrl
        print(f"  Simulated Result URL: {simulated_result_url}")
        print("-" * 20)
        # --- END SIMULATION ---

        if not simulated_result_url:
             # Handle case where clothing item might not have an image URL
             print("Try-on Warning: Clothing item has no imageUrl to use for simulation.")
             # You might return a default placeholder image URL here instead
             return jsonify({
                 "message": "Try-on processed (simulated), but clothing item has no image.",
                 "resultImageUrl": None # Or a placeholder URL
                 }), 200


        return jsonify({
            "message": "Try-on generated successfully (simulated).",
            "resultImageUrl": simulated_result_url
            }), 200

    except Exception as e:
        print(f"Error during try-on processing: {e}")
        # Log the full exception for debugging if needed:
        # import traceback
        # print(traceback.format_exc())
        return jsonify({"error": "An internal error occurred during try-on processing"}), 500
# -------------------------

# --- Database Initialization Command (Optional but Recommended) ---
# You can run this once from the Flask shell to create tables
# In your terminal (with venv activated):
# > flask shell
# >>> from app import db
# >>> db.create_all()
# >>> exit()
# -----------------------------------------------------------------

# Add other routes later...

if __name__ == '__main__':
    app.run(debug=True) # Keep debug=True for development
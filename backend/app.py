# backend/app.py
import os
import logging # Import logging
from logging.handlers import RotatingFileHandler # For rotating logs
from flask import Flask, jsonify, request # Import request
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from werkzeug.utils import secure_filename # Import secure_filename
from sqlalchemy import distinct # Import distinct
from PIL import Image # Import Pillow
import requests       # To download image from URL
import io             # To handle image data from requests

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
CORS(app)

# --- Logging Configuration ---
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True) # Create logs directory if it doesn't exist
log_file = os.path.join(log_dir, 'backend.log')

# Use RotatingFileHandler to limit log file size
# Max 10MB per file, keep 5 backup files
file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*10, backupCount=5)
file_handler.setLevel(logging.INFO) # Set level for file logging (e.g., INFO, DEBUG)

# Define log format
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
file_handler.setFormatter(formatter)

# Add handler to the Flask app's logger
# Remove default handlers if necessary to avoid duplicate console output when debug=True
# app.logger.handlers.clear() # Optional: Uncomment if you ONLY want file logging
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO) # Set overall level for the app logger

app.logger.info('Backend application starting up...') # Log startup
# --------------------------

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
        if brand_filter:
            query = query.filter_by(brand=brand_filter)
            app.logger.info(f"Filtering catalog for brand: {brand_filter}") # Use logger

        # Execute the final query (either filtered or unfiltered)
        items = query.all()

        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        app.logger.exception(f"Error fetching catalog: {e}") # Use logger.exception
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

# --- UPDATED TRY-ON ENDPOINT ---
@app.route('/api/tryon', methods=['POST'])
def process_tryon():
    """
    (Simulated) Processes a virtual try-on request using Pillow for basic inspection.
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

        # --- SIMULATED TRY-ON PROCESSING (with Pillow example) ---
        print("-" * 20)
        print(f"Simulating Try-On (using Pillow):")
        print(f"  User Image Path: {user_image_path}")
        print(f"  Clothing Item: ID={clothing_item.id}, Name='{clothing_item.name}', Image='{clothing_item.imageUrl}'")

        user_img = None
        clothing_img = None

        try:
            # 3. Load user image with Pillow
            user_img = Image.open(user_image_path)
            # Ensure image is in RGB mode for consistency (optional, depends on model needs)
            # user_img = user_img.convert("RGB")
            print(f"  User Image Info: Format={user_img.format}, Size={user_img.size}, Mode={user_img.mode}")

            # 4. Load clothing image (assuming imageUrl is a downloadable URL)
            if clothing_item.imageUrl:
                try:
                    print(f"  Attempting to download clothing image from: {clothing_item.imageUrl}")
                    # Use a timeout for the request
                    response = requests.get(clothing_item.imageUrl, stream=True, timeout=15)
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                    # Check content type (optional but good practice)
                    content_type = response.headers.get('content-type')
                    if content_type and 'image' in content_type.lower():
                        # Open image directly from response content using io.BytesIO
                        clothing_img = Image.open(io.BytesIO(response.content))
                        # clothing_img = clothing_img.convert("RGBA") # Convert to RGBA if transparency needed
                        print(f"  Clothing Image Info: Format={clothing_img.format}, Size={clothing_img.size}, Mode={clothing_img.mode}")
                    else:
                         print(f"  Warning: URL did not return an image content-type (got '{content_type}'). Skipping clothing image load.")

                except requests.exceptions.RequestException as req_err:
                    print(f"  Warning: Could not download clothing image from URL ({clothing_item.imageUrl}): {req_err}")
                except Exception as img_err:
                     print(f"  Warning: Could not load clothing image from URL ({clothing_item.imageUrl}) with Pillow: {img_err}")
            else:
                print("  Warning: Clothing item has no imageUrl.")

            # --- Placeholder for actual image manipulation using user_img and clothing_img ---
            # This is where you would use Pillow functions like resize, paste, filter, etc.
            # based on the logic of your chosen try-on method.
            # Example:
            # if user_img and clothing_img:
            #    # Simple resize and paste (no alignment, just demonstration)
            #    resized_clothing = clothing_img.resize((user_img.width // 3, user_img.height // 3))
            #    paste_x = (user_img.width - resized_clothing.width) // 2
            #    paste_y = (user_img.height - resized_clothing.height) // 2
            #    # Create a copy to avoid modifying the original loaded image
            #    result_img = user_img.copy()
            #    # Use clothing image itself as mask if it has alpha (RGBA), otherwise no mask
            #    mask = resized_clothing if resized_clothing.mode == 'RGBA' else None
            #    result_img.paste(resized_clothing, (paste_x, paste_y), mask=mask)
            #    # Now you would save result_img and generate its URL
            #    # result_img.save(result_save_path)
            #    # real_result_url = ...
            # ---------------------------------------------------------------------------------

        except Exception as pil_err:
            # Log errors during Pillow processing but don't necessarily stop the simulation
            print(f"  Error during Pillow processing: {pil_err}")

        # For now, just return the original clothing item's URL as the "result"
        simulated_result_url = clothing_item.imageUrl
        print(f"  Simulated Result URL (unchanged): {simulated_result_url}")
        print("-" * 20)
        # --- END SIMULATION ---

        if not simulated_result_url:
             print("Try-on Warning: Clothing item has no imageUrl to use for simulation.")
             return jsonify({
                 "message": "Try-on processed (simulated), but clothing item has no image.",
                 "resultImageUrl": None
                 }), 200

        return jsonify({
            "message": "Try-on generated successfully (simulated).",
            "resultImageUrl": simulated_result_url
            }), 200

    except Exception as e:
        print(f"Error during try-on processing: {e}")
        # import traceback
        # print(traceback.format_exc()) # Uncomment for detailed debugging
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
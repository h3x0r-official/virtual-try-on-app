# backend/app.py
import os
import logging # Import logging
import time    # Import time module for timestamps
from logging.handlers import RotatingFileHandler # For rotating logs
from flask import Flask, jsonify, request, send_from_directory # Import request and send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from werkzeug.utils import secure_filename # Import secure_filename
from sqlalchemy import distinct # Import distinct
from PIL import Image # Import Pillow
import requests       # To download image from URL
import io             # To handle image data from requests
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import cv2
import numpy as np
import mediapipe as mp
from remove_bg import remove_background

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
# Secret key for session management (required by Flask-Admin)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
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
# Set up SQLite database path and URI
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Flask-Admin Configuration ---
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
# -----------------------------

# --- Flask-Admin Configuration ---
admin = Admin(app, name='Virtual Try-On Admin', template_mode='bootstrap3')
admin.add_view(ModelView(ClothingItem, db.session))
# -----------------------------

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
    Processes a virtual try-on request using MediaPipe for pose detection and Pillow for compositing.
    Expects JSON body with 'userImageFilename' and either 'clothingImageUrl' (preferred) or 'clothingItemId'.
    Returns a result image URL.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_image_filename = data.get('userImageFilename')
    clothing_image_url = data.get('clothingImageUrl')
    clothing_item_id = data.get('clothingItemId')

    if not user_image_filename or (not clothing_image_url and not clothing_item_id):
        return jsonify({"error": "Missing 'userImageFilename' and either 'clothingImageUrl' or 'clothingItemId' in request body"}), 400

    try:
        user_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(user_image_filename))
        if not os.path.exists(user_image_path):
            return jsonify({"error": f"User image '{user_image_filename}' not found on server"}), 404

        # --- Get clothing image ---
        clothing_img = None
        if clothing_image_url and clothing_image_url.startswith('/uploads/'):
            # Use local file from uploads
            clothing_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(clothing_image_url))
            if not os.path.exists(clothing_path):
                return jsonify({"error": f"Clothing image '{clothing_image_url}' not found on server"}), 404
            clothing_img = Image.open(clothing_path).convert("RGBA")
        elif clothing_item_id:
            clothing_item = ClothingItem.query.get(clothing_item_id)
            if not clothing_item or not clothing_item.imageUrl:
                return jsonify({"error": f"Clothing item with ID {clothing_item_id} not found or missing imageUrl"}), 404
            response = requests.get(clothing_item.imageUrl, stream=True, timeout=15)
            response.raise_for_status()
            clothing_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            clothing_img = remove_background(clothing_img)
        else:
            return jsonify({"error": "No valid clothing image source provided."}), 400

        # Load user image
        user_img = Image.open(user_image_path).convert("RGBA")
        user_img_np = np.array(user_img)
        user_img_rgb = cv2.cvtColor(user_img_np, cv2.COLOR_RGBA2RGB)

        # MediaPipe pose detection
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, model_complexity=1, enable_segmentation=False) as pose:
            results = pose.process(user_img_rgb)
            if not results.pose_landmarks:
                return jsonify({"error": "Could not detect pose landmarks in user image."}), 422

            # Extract key landmarks
            lm = results.pose_landmarks.landmark
            left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
            # Use image size to get pixel coordinates
            h, w, _ = user_img_rgb.shape
            x1, y1 = int(left_shoulder.x * w), int(left_shoulder.y * h)
            x2, y2 = int(right_shoulder.x * w), int(right_shoulder.y * h)
            x3, y3 = int(left_hip.x * w), int(left_hip.y * h)
            x4, y4 = int(right_hip.x * w), int(right_hip.y * h)
            # Compute bounding box for torso
            min_x = min(x1, x2, x3, x4)
            max_x = max(x1, x2, x3, x4)
            min_y = min(y1, y2)
            max_y = max(y3, y4)
            box_width = max_x - min_x
            box_height = max_y - min_y
            # Resize clothing image to fit the bounding box
            aspect = clothing_img.height / clothing_img.width
            target_width = box_width
            target_height = int(target_width * aspect)
            if target_height > box_height:
                target_height = box_height
                target_width = int(target_height / aspect)
            clothing_resized = clothing_img.resize((target_width, target_height), Image.LANCZOS)
            # Center clothing horizontally in the box, align top to min_y
            paste_x = min_x + (box_width - target_width) // 2
            paste_y = min_y
            # Composite
            result_img = user_img.copy()
            result_img.paste(clothing_resized, (paste_x, paste_y), mask=clothing_resized)

        # Save result
        result_filename = f"tryon_{os.path.splitext(user_image_filename)[0]}_{os.path.basename(clothing_image_url) if clothing_image_url else clothing_item_id}.png"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        result_img.save(result_path)
        result_url = f"/uploads/{result_filename}"
        return jsonify({
            "message": "Try-on generated successfully.",
            "resultImageUrl": result_url
            }), 200

    except Exception as e:
        print(f"Error during try-on processing: {e}")
        return jsonify({"error": "An internal error occurred during try-on processing"}), 500
# -------------------------

# --- NEW REMOVE-BG ENDPOINT ---
@app.route('/api/remove-bg', methods=['POST'])
def remove_bg_endpoint():
    data = request.get_json()
    image_url = data.get('imageUrl')
    if not image_url:
        return jsonify({"error": "Missing imageUrl"}), 400

    try:
        response = requests.get(image_url, stream=True, timeout=15)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        img_no_bg = remove_background(img)

        # Save and return the new image URL
        filename = f"nobg_{os.path.splitext(os.path.basename(image_url).split('?')[0])[0]}.png"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img_no_bg.save(save_path, format="PNG")
        return jsonify({"resultImageUrl": f"/uploads/{filename}"})
    except Exception as e:
        return jsonify({"error": f"Failed to remove background: {str(e)}"}), 500
# -------------------------

# --- Database Initialization Command (Optional but Recommended) ---
# You can run this once from the Flask shell to create tables
# In your terminal (with venv activated):
# > flask shell
# >>> from app import db
# >>> db.create_all()
# >>> exit()
# -----------------------------------------------------------------

# --- NEW LIVE TRY-ON ENDPOINT ---
@app.route('/api/live-tryon', methods=['POST'])
def process_live_tryon():
    """
    Processes a live webcam frame for virtual try-on.
    Expects 'frame' (image file) and 'clothingItemId' in multipart/form-data.
    Returns a processed image with clothing overlaid.
    """
    if 'frame' not in request.files:
        return jsonify({"error": "No frame part in the request"}), 400

    frame_file = request.files['frame']
    clothing_item_id = request.form.get('clothingItemId')

    if not clothing_item_id:
        return jsonify({"error": "Missing clothingItemId parameter"}), 400

    if frame_file.filename == '':
        return jsonify({"error": "No frame provided"}), 400

    try:
        # Save the frame temporarily
        temp_frame_filename = f"temp_frame_{int(time.time())}.jpg"
        temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_frame_filename)
        frame_file.save(temp_frame_path)
        
        # Get clothing item
        clothing_item = ClothingItem.query.get(clothing_item_id)
        if not clothing_item or not clothing_item.imageUrl:
            os.remove(temp_frame_path)  # Clean up temp file
            return jsonify({"error": f"Clothing item with ID {clothing_item_id} not found or missing imageUrl"}), 404
            
        # Download and process clothing image
        response = requests.get(clothing_item.imageUrl, stream=True, timeout=15)
        response.raise_for_status()
        clothing_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        clothing_img = remove_background(clothing_img)
        
        # Process the webcam frame
        user_img = Image.open(temp_frame_path).convert("RGBA")
        user_img_np = np.array(user_img)
        user_img_rgb = cv2.cvtColor(user_img_np, cv2.COLOR_RGBA2RGB)
        
        # MediaPipe pose detection
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, model_complexity=1, enable_segmentation=False) as pose:
            results = pose.process(user_img_rgb)
            
            if not results.pose_landmarks:
                os.remove(temp_frame_path)  # Clean up temp file
                return jsonify({"error": "Could not detect pose landmarks in frame"}), 422
            
            # Extract key landmarks (same as regular try-on)
            lm = results.pose_landmarks.landmark
            left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
            
            # Calculate positioning
            h, w, _ = user_img_rgb.shape
            x1, y1 = int(left_shoulder.x * w), int(left_shoulder.y * h)
            x2, y2 = int(right_shoulder.x * w), int(right_shoulder.y * h)
            x3, y3 = int(left_hip.x * w), int(left_hip.y * h)
            x4, y4 = int(right_hip.x * w), int(right_hip.y * h)
            
            # Compute bounding box for torso
            min_x = min(x1, x2, x3, x4)
            max_x = max(x1, x2, x3, x4)
            min_y = min(y1, y2)
            max_y = max(y3, y4)
            box_width = max_x - min_x
            box_height = max_y - min_y
            
            # Resize clothing image to fit the bounding box
            aspect = clothing_img.height / clothing_img.width
            target_width = box_width
            target_height = int(target_width * aspect)
            if target_height > box_height:
                target_height = box_height
                target_width = int(target_height / aspect)
                
            clothing_resized = clothing_img.resize((target_width, target_height), Image.LANCZOS)
            
            # Center clothing horizontally in the box, align top to min_y
            paste_x = min_x + (box_width - target_width) // 2
            paste_y = min_y
            
            # Composite
            result_img = user_img.copy()
            result_img.paste(clothing_resized, (paste_x, paste_y), mask=clothing_resized)
        
        # Save result
        result_filename = f"live_tryon_{int(time.time())}.png"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        result_img.save(result_path)
        
        # Clean up temporary frame
        os.remove(temp_frame_path)
        
        # Return the result URL
        result_url = f"/uploads/{result_filename}"
        return jsonify({
            "message": "Live try-on processed successfully",
            "resultImageUrl": result_url
        }), 200
        
    except Exception as e:
        app.logger.exception(f"Error during live try-on processing: {e}")
        # Clean up temporary files if they exist
        if 'temp_frame_path' in locals() and os.path.exists(temp_frame_path):
            os.remove(temp_frame_path)
        return jsonify({"error": f"An internal error occurred during live try-on processing: {str(e)}"}), 500
# -------------------------

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Add other routes later...

if __name__ == '__main__':
    app.run(debug=True) # Keep debug=True for development
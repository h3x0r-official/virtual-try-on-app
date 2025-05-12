# backend/app.py
import os
import logging # Import logging
import time    # Import time module for timestamps
import random  # For probabilistic cache cleaning
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
    # Initialize time tracking for performance monitoring
    start_time = time.time()
    
    # Rate limiting - check client IP and limit requests
    # This is a simple implementation; in production, use Redis or a proper rate limiter
    client_ip = request.remote_addr
    current_time = time.time()
    
    # Simple in-memory rate limiting (not suitable for production with multiple workers)
    if not hasattr(app, 'rate_limit_store'):
        app.rate_limit_store = {}
    
    # If more than 5 requests in 2 seconds from same IP, throttle
    if client_ip in app.rate_limit_store:
        requests_history = [t for t in app.rate_limit_store[client_ip] if current_time - t < 2.0]
        if len(requests_history) >= 5:
            app.logger.warning(f"Rate limiting applied to {client_ip}")
            return jsonify({"error": "Too many requests. Please slow down."}), 429
        app.rate_limit_store[client_ip] = requests_history + [current_time]
    else:
        app.rate_limit_store[client_ip] = [current_time]
    
    # Input validation
    if 'frame' not in request.files:
        return jsonify({"error": "No frame part in the request"}), 400

    frame_file = request.files['frame']
    clothing_item_id = request.form.get('clothingItemId')

    if not clothing_item_id:
        return jsonify({"error": "Missing clothingItemId parameter"}), 400

    if frame_file.filename == '':
        return jsonify({"error": "No frame provided"}), 400

    # Create a unique temporary filename with a timestamp
    temp_frame_filename = None
    temp_frame_path = None
    
    try:
        # Save the frame temporarily with a unique name to prevent conflicts
        timestamp = int(time.time() * 1000)  # Milliseconds for better uniqueness
        temp_frame_filename = f"temp_frame_{timestamp}_{os.urandom(4).hex()}.jpg"
        temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_frame_filename)
        frame_file.save(temp_frame_path)
        
        app.logger.debug(f"Frame saved to {temp_frame_path}")
        
        # Get clothing item
        clothing_item = ClothingItem.query.get(clothing_item_id)
        if not clothing_item or not clothing_item.imageUrl:
            os.remove(temp_frame_path)  # Clean up temp file
            return jsonify({"error": f"Clothing item with ID {clothing_item_id} not found or missing imageUrl"}), 404
        
        # Initialize clothing image cache if it doesn't exist
        if not hasattr(app, 'clothing_cache'):
            app.clothing_cache = {}
            
        # Check if we've already processed this clothing image
        cache_key = f"clothing_{clothing_item_id}"
        if cache_key in app.clothing_cache:
            clothing_img = app.clothing_cache[cache_key]
            app.logger.debug(f"Using cached clothing image for item {clothing_item_id}")
        else:
            # Download and process clothing image
            try:
                response = requests.get(clothing_item.imageUrl, stream=True, timeout=10)
                response.raise_for_status()
                clothing_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
                
                # Process and remove background
                clothing_img = remove_background(clothing_img)
                
                # Cache the processed image for future frames
                app.clothing_cache[cache_key] = clothing_img
                app.logger.debug(f"Cached clothing image for item {clothing_item_id}")
            except requests.exceptions.RequestException as req_err:
                os.remove(temp_frame_path)  # Clean up temp file
                app.logger.error(f"Failed to download clothing image: {req_err}")
                return jsonify({"error": "Failed to download clothing image"}), 502
        
        # Process the webcam frame
        try:
            # Use OpenCV for faster image processing
            user_img_cv = cv2.imread(temp_frame_path)
            if user_img_cv is None:
                raise ValueError("Failed to read image file")
            
            # Convert to RGB for MediaPipe
            user_img_rgb = cv2.cvtColor(user_img_cv, cv2.COLOR_BGR2RGB)
            
            # For PIL operations later, also load with PIL
            user_img = Image.open(temp_frame_path).convert("RGBA")
            
            # Get image dimensions
            h, w = user_img_rgb.shape[:2]
            
            # Detect pose landmarks
            mp_pose = mp.solutions.pose
            # Use lower model complexity for speed in live mode
            pose_config = {
                'static_image_mode': False,  # Switch to video mode for better tracking
                'model_complexity': 0,       # Use lightweight model (0, 1, or 2)
                'smooth_landmarks': True,    # Temporal smoothing for better stability
                'min_detection_confidence': 0.5,
                'min_tracking_confidence': 0.5
            }
            
            with mp_pose.Pose(**pose_config) as pose:
                # Process frame
                start_pose_detection = time.time()
                results = pose.process(user_img_rgb)
                pose_detection_time = time.time() - start_pose_detection
                app.logger.debug(f"Pose detection completed in {pose_detection_time:.3f}s")
                
                if not results.pose_landmarks:
                    os.remove(temp_frame_path)  # Clean up temp file
                    return jsonify({"error": "Could not detect pose landmarks in frame"}), 422
                
                # Extract key landmarks for torso
                lm = results.pose_landmarks.landmark
                left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
                
                # Calculate positioning
                x1, y1 = int(left_shoulder.x * w), int(left_shoulder.y * h)
                x2, y2 = int(right_shoulder.x * w), int(right_shoulder.y * h)
                x3, y3 = int(left_hip.x * w), int(left_hip.y * h)
                x4, y4 = int(right_hip.x * w), int(right_hip.y * h)
                
                # Compute bounding box for torso with padding
                min_x = max(0, min(x1, x2) - int(w * 0.02))      # Add 2% width as padding
                max_x = min(w, max(x1, x2, x3, x4) + int(w * 0.02))
                min_y = max(0, min(y1, y2) - int(h * 0.02))      # Add 2% height as padding
                max_y = min(h, max(y3, y4) + int(h * 0.02))
                
                box_width = max_x - min_x
                box_height = max_y - min_y
                
                # If torso detection looks unreasonable, use fallback dimensions
                if box_width < 20 or box_height < 50 or box_width / box_height > 2.5:
                    app.logger.warning("Unusual torso dimensions detected, using fallback values")
                    # Fallback to center with reasonable dimensions
                    min_x = w // 4
                    max_x = min_x + w // 2
                    min_y = h // 4
                    max_y = min_y + h // 2
                    box_width = max_x - min_x
                    box_height = max_y - min_y
                
                # Resize clothing image efficiently 
                aspect = clothing_img.height / clothing_img.width
                target_width = box_width
                target_height = int(target_width * aspect)
                
                # Ensure clothing fits in the detection box
                if target_height > box_height:
                    target_height = box_height
                    target_width = int(target_height / aspect)
                
                # Use BILINEAR for better performance (LANCZOS is higher quality but slower)
                clothing_resized = clothing_img.resize((target_width, target_height), Image.BILINEAR)
                
                # Center clothing horizontally in box, align top with shoulders
                paste_x = min_x + (box_width - target_width) // 2
                paste_y = min_y
                
                # Composite images
                result_img = user_img.copy()
                result_img.paste(clothing_resized, (paste_x, paste_y), mask=clothing_resized)
                
                # Track how many live results we've generated and manage them
                if not hasattr(app, 'live_results_count'):
                    app.live_results_count = 0
                
                # Generate result filename
                result_filename = f"live_tryon_{int(time.time())}_{os.urandom(3).hex()}.png"
                result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
                
                # Save as JPEG for smaller file size (unless transparency needed)
                result_img.save(result_path, format="PNG", optimize=True)
                
                # Increment counter and clean old results if too many
                app.live_results_count += 1
                if app.live_results_count > 100:  # Keep only the latest 100 results
                    app.logger.info("Cleaning up old live try-on results")
                    try:
                        # Find and remove old live try-on files
                        upload_dir = app.config['UPLOAD_FOLDER']
                        live_tryon_files = sorted([f for f in os.listdir(upload_dir) 
                                                  if f.startswith('live_tryon_')])
                        # Delete oldest files except the most recent 50
                        for old_file in live_tryon_files[:-50]:
                            os.remove(os.path.join(upload_dir, old_file))
                        app.live_results_count = 50  # Reset counter
                    except Exception as cleanup_err:
                        app.logger.error(f"Error cleaning up old files: {cleanup_err}")
                
                # Clean up the temporary frame
                try:
                    os.remove(temp_frame_path)
                except Exception as rm_err:
                    app.logger.warning(f"Failed to remove temp file {temp_frame_path}: {rm_err}")
                
                # Return the result URL
                result_url = f"/uploads/{result_filename}"
                
                # Log performance metrics
                total_time = time.time() - start_time
                app.logger.info(f"Live try-on completed in {total_time:.3f}s")
        
        except Exception as processing_err:
            app.logger.exception(f"Error processing frame: {processing_err}")
            if temp_frame_path and os.path.exists(temp_frame_path):
                os.remove(temp_frame_path)
            return jsonify({"error": f"Error processing frame: {str(processing_err)}"}), 500
        # Include performance info and result URL in response
        return jsonify({
            "message": "Live try-on processed successfully",
            "resultImageUrl": result_url,
            "processingTimeMs": int((time.time() - start_time) * 1000)
        }), 200
        
    except Exception as e:
        app.logger.exception(f"Error during live try-on processing: {e}")
        
        # Clean up temporary files if they exist
        if temp_frame_path and os.path.exists(temp_frame_path):
            try:
                os.remove(temp_frame_path)
            except Exception as rm_err:
                app.logger.error(f"Failed to remove temp file during error handling: {rm_err}")
        
        # Provide appropriate error message based on exception type
        if isinstance(e, (requests.exceptions.RequestException, requests.exceptions.Timeout)):
            return jsonify({"error": "Network error accessing clothing image"}), 502
        elif isinstance(e, (OSError, IOError)):
            return jsonify({"error": "File system error processing images"}), 500
        elif isinstance(e, ValueError) and "landmarks" in str(e).lower():
            return jsonify({"error": "Could not detect proper body pose in the frame"}), 422
        else:
            return jsonify({
                "error": f"An internal error occurred during live try-on processing: {str(e)}",
                "errorType": e.__class__.__name__
            }), 500
# -------------------------

# Utility function to clear old cache entries
def clear_old_cache(max_items=50):
    """Clear old entries from our in-memory caches to prevent memory bloat"""
    if hasattr(app, 'clothing_cache') and len(app.clothing_cache) > max_items:
        app.logger.info(f"Cleaning clothing cache ({len(app.clothing_cache)} items)")
        # Convert to list to avoid mutation during iteration
        items = list(app.clothing_cache.items())
        # Remove oldest items, keeping the newest max_items
        for key, _ in items[:-max_items]:
            app.clothing_cache.pop(key, None)
            
    if hasattr(app, 'rate_limit_store'):
        # Clear old rate limit entries (older than 1 hour)
        current_time = time.time()
        cleaned_store = {}
        for ip, timestamps in app.rate_limit_store.items():
            # Keep only timestamps within the last hour
            recent_timestamps = [t for t in timestamps if current_time - t < 3600]
            if recent_timestamps:  # If any timestamps remain
                cleaned_store[ip] = recent_timestamps
        app.rate_limit_store = cleaned_store

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Occasionally clean caches when serving files
    if random.random() < 0.05:  # 5% chance to run cleanup
        clear_old_cache()
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Cache management endpoint (admin only)
@app.route('/api/admin/clear-cache', methods=['POST'])
def clear_cache():
    # In production, add authentication check here
    if not app.debug:
        # Simple security check - only allow from localhost in production
        if request.remote_addr not in ('127.0.0.1', 'localhost'):
            return jsonify({"error": "Unauthorized access"}), 403
    
    # Clear all caches
    if hasattr(app, 'clothing_cache'):
        cache_size = len(app.clothing_cache)
        app.clothing_cache.clear()
    else:
        cache_size = 0
        app.clothing_cache = {}
        
    if hasattr(app, 'rate_limit_store'):
        app.rate_limit_store.clear()
        
    if hasattr(app, 'live_results_count'):
        app.live_results_count = 0
        
    return jsonify({
        "message": f"All caches cleared. Removed {cache_size} clothing cache items.",
        "success": True
    })

# Add other routes later...

if __name__ == '__main__':
    app.run(debug=True) # Keep debug=True for development
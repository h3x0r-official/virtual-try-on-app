# Virtual Try-On Application Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Installation Guide](#installation-guide)
   - [System Requirements](#system-requirements)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
3. [User Guide](#user-guide)
   - [Photo Upload Try-On](#photo-upload-try-on)
   - [Live Webcam Try-On](#live-webcam-try-on)
   - [Browsing the Catalog](#browsing-the-catalog)
4. [Admin Guide](#admin-guide)
   - [Accessing the Admin Interface](#accessing-the-admin-interface)
   - [Managing the Catalog](#managing-the-catalog)
   - [System Maintenance](#system-maintenance)
5. [Developer Guide](#developer-guide)
   - [API Documentation](#api-documentation)
   - [Code Structure](#code-structure)
   - [Extending the Application](#extending-the-application)
6. [Troubleshooting](#troubleshooting)
   - [Common User Issues](#common-user-issues)
   - [Webcam Problems](#webcam-problems)
   - [Backend Issues](#backend-issues)
7. [Security Considerations](#security-considerations)
8. [FAQs](#faqs)

---

## Introduction

The Virtual Try-On Web Application allows users to virtually try on clothing items through two methods:

1. **Photo Upload**: Upload a photo and see clothing items overlaid on your picture
2. **Live Webcam**: Use your device's webcam for real-time virtual try-on experience

The application consists of a React frontend and Flask backend, with virtual try-on technology that uses computer vision to identify body landmarks and overlay clothing items realistically.

---

## Installation Guide

### System Requirements

**Backend Requirements:**
- Python 3.8 or later
- 4GB RAM minimum (8GB+ recommended for concurrent users)
- 1GB free disk space
- Internet connection for initial setup

**Frontend Requirements:**
- Node.js 16.x or later
- npm 8.x or later
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/h3x0r-official/virtual-try-on-app.git
   cd virtual-try-on-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```

5. **Create required directories:**
   ```bash
   mkdir -p uploads logs
   ```

6. **Start the backend server:**
   ```bash
   python app.py
   ```
   The backend will be available at http://127.0.0.1:5000

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application will be available at http://localhost:5173

4. **For production deployment:**
   ```bash
   npm run build
   ```
   This creates optimized files in the `dist` folder that can be served by any static web server.

---

## User Guide

### Photo Upload Try-On

1. **Access the application** at http://localhost:5173 (or your configured URL)
2. **Ensure the "Photo Try-On" tab is selected** (default)
3. **Upload your photo:**
   - Click the "Choose File" button
   - Select a clear, front-facing photo where your full upper body is visible
   - The selected photo will appear in the preview area
   - Click "Upload" to process your photo
4. **Select a clothing item:**
   - Browse the catalog on the right side
   - You can filter by brand using the dropdown
   - Click on an item card to select it for try-on
5. **View the try-on result:**
   - After selecting an item, the system will process and display the virtual try-on result
   - You can click on different items to see how they look on your uploaded photo

### Live Webcam Try-On

1. **Click the "Live Try-On" tab** at the top of the application
2. **Allow webcam access** when prompted by your browser
3. **Position yourself** in the webcam frame:
   - Ensure good lighting conditions
   - Stand at a distance where your upper body is fully visible
   - Face the camera directly for best results
4. **Select a clothing item** from the catalog on the right
5. **View the live try-on:**
   - The selected clothing item will be overlaid on your webcam feed in real-time
   - You can move slightly to see how the virtual clothing follows your movements
   - The processing happens at regular intervals to maintain performance

**Troubleshooting Webcam Issues:**
- If the webcam doesn't start automatically, click the "Start Webcam" button
- If you're having autoplay issues, try the "Force Play" button
- Make sure no other applications are using your webcam
- Check browser permissions if the webcam doesn't start

### Browsing the Catalog

1. **View all items** in the catalog by default
2. **Filter by brand:**
   - Use the dropdown menu at the top
   - Select a specific brand or "All Brands"
3. **Each item card displays:**
   - Product image
   - Item name
   - Price
   - Brand name
4. **Select an item** by clicking on its card to use it for try-on

---

## Admin Guide

### Accessing the Admin Interface

1. **Navigate to** http://127.0.0.1:5000/admin in your web browser
2. **Log in** with your admin credentials (if configured)

### Managing the Catalog

1. **View catalog items:**
   - All items are listed in a table format
   - You can sort by clicking on column headers

2. **Add a new item:**
   - Click the "Create" button
   - Fill in the required fields:
     - Name
     - Price
     - Image URL (direct link to clothing image)
     - Brand
   - Click "Save" to add the item to the catalog

3. **Edit an existing item:**
   - Click on the item's row
   - Update the information
   - Click "Save" to apply changes

4. **Delete an item:**
   - Click on the item's row
   - Click the "Delete" button
   - Confirm deletion

### System Maintenance

1. **Clear application cache:**
   - Send a POST request to `/api/admin/clear-cache`
   - This endpoint is restricted to localhost access in production mode
   - Clears image caches, rate limiting data, and result counters

2. **Monitor logs:**
   - Backend logs are stored in the `backend/logs` directory
   - Use log rotation to manage file sizes
   - Check `backend.log` for application errors and diagnostics

3. **Manage uploads directory:**
   - User uploads are stored in `backend/uploads`
   - The system automatically cleans up old files
   - You can manually delete files if storage becomes an issue

---

## Developer Guide

### API Documentation

Complete API documentation is available in the `backend/API_DOCUMENTATION.md` file. Key endpoints include:

1. **Health Check:**
   - `GET /api/hello` - Confirms the backend is running

2. **Catalog Management:**
   - `GET /api/catalog` - Retrieves the clothing catalog
   - `GET /api/brands` - Lists available brands

3. **Try-On Processing:**
   - `POST /api/upload` - Uploads a user photo
   - `POST /api/tryon` - Processes try-on for uploaded photos
   - `POST /api/live-tryon` - Processes webcam frames for live try-on

4. **Admin Endpoints:**
   - `POST /api/admin/clear-cache` - Clears application caches

### Code Structure

**Backend Structure:**
- `app.py` - Main Flask application with API endpoints and admin panel
- `requirements.txt` - Python dependencies
- `database.sqlite` - SQLite database file
- `uploads/` - Directory for user uploaded images and try-on results
- `logs/` - Application log files

**Frontend Structure:**
- `src/components/` - React component files
- `src/App.jsx` - Main application component
- `src/components/LiveTryOn.jsx` - Webcam try-on component
- `src/components/CatalogItemCard.jsx` - Catalog item display

### Extending the Application

**Adding New Features:**

1. **New Clothing Categories:**
   - Modify the database schema in `app.py`
   - Update the catalog filtering logic in the frontend
   - Add new fields to the admin interface

2. **Enhanced Try-On Features:**
   - Improve the `process_frame` function in the backend for better overlay
   - Add body pose filters in the `mediapipe` implementation
   - Consider implementing a full ML model for more realistic try-on

3. **User Accounts:**
   - Add Flask-Login for user authentication
   - Create user profile pages
   - Implement favorites/history features

---

## Troubleshooting

### Common User Issues

1. **Images not loading:**
   - Check internet connection
   - Verify the image URLs in the database
   - Clear browser cache

2. **Upload errors:**
   - Ensure file is a supported format (JPEG, PNG, GIF)
   - Check file size (should be under 10MB)
   - Verify the uploads directory has write permissions

3. **Try-on not working:**
   - Make sure the photo shows a clear, front-facing pose
   - Check that the clothing item has a valid image URL
   - Retry with a different photo or clothing item

### Webcam Problems

1. **Webcam won't start:**
   - Check browser permissions (look for camera icon in address bar)
   - Make sure no other application is using the webcam
   - Try the "Force Play" button for autoplay issues
   - Refresh the page and try again

2. **Poor try-on quality:**
   - Improve lighting conditions (avoid backlighting)
   - Stand at an appropriate distance from the camera
   - Wear plain, solid-color clothing for better detection
   - Ensure your face and upper body are clearly visible

3. **Performance issues:**
   - Close other browser tabs and applications
   - Check your internet connection speed
   - Try a different browser (Chrome or Firefox recommended)

### Backend Issues

1. **Server won't start:**
   - Check if required ports are available (default: 5000)
   - Verify Python version (3.8+ required)
   - Check logs for specific errors

2. **Database errors:**
   - Make sure `database.sqlite` exists and is not corrupted
   - Run `init_db.py` to reset the database if necessary
   - Check file permissions

3. **Rate limiting or slow performance:**
   - Clear the application cache using the admin endpoint
   - Restart the server
   - Check server resource usage (CPU, RAM)

---

## Security Considerations

1. **File Uploads:**
   - The system validates file types and sanitizes filenames
   - Uploaded files are stored separately from application code
   - Regular cleanup prevents excessive storage usage

2. **Admin Access:**
   - Admin endpoints are restricted to localhost in production mode
   - Deploy behind a secure reverse proxy in production
   - Use HTTPS for all connections

3. **Data Privacy:**
   - User photos are processed locally on the server
   - No automatic cloud storage of user images
   - Consider implementing automatic deletion of user photos after processing

---

## FAQs

**Q: How accurate is the virtual try-on?**  
A: The current implementation offers a simulated preview with reasonable positioning based on body landmarks. It's meant for visualization rather than a perfect representation of fit.

**Q: Can I try on any type of clothing?**  
A: The current system works best with upper body clothing like shirts, t-shirts, and jackets. Full-body try-on would require additional development.

**Q: How many users can use the application simultaneously?**  
A: The default configuration supports 5-10 concurrent users with reasonable performance. For higher loads, consider scaling the backend or implementing a queue system.

**Q: Is my photo data safe?**  
A: Yes. Your photos are processed locally on the server and not shared with third parties. We recommend deploying with HTTPS to ensure secure transmission.

**Q: Can I integrate this with my e-commerce store?**  
A: Yes, the application is designed to be extensible. The API can be integrated with existing e-commerce platforms with additional development work.

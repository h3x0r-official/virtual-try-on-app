# Virtual Try-On Web App

This project aims to create a web application allowing users to virtually try on clothes using 2D image overlays.

## Project Structure

- `/frontend`: Contains the React frontend application (built with Vite).
- `/backend`: Contains the Python/Flask backend API for image processing and data management.

## Setup

### Frontend

cd frontend
npm install
npm run dev

### Backend

cd backend
python -m venv .venv

## Activate virtual environment (see OS-specific commands):

- Windows (Git Bash/WSL): source .venv/Scripts/activate
- Windows (Cmd/PS): .venv\Scripts\activate
- macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
export FLASK_APP=app.py # or use .flaskenv
flask run
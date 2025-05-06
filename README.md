# Virtual Try-On Web Application

This project is a web application that allows users to upload their photo and virtually try on clothing items from a catalog. It features a React frontend and a Flask (Python) backend with a PostgreSQL database.

## Features

* **User Image Upload:** Users can upload their photos.
* **Clothing Catalog:** Browse a catalog of clothing items, filterable by brand.
* **Virtual Try-On (Simulated):** Select an uploaded photo and a clothing item to generate a simulated try-on image. (Currently, the backend simulates this by returning the clothing item's image).
* **Dynamic Frontend:** User interface built with React for a responsive experience.
* **Backend API:** RESTful API built with Flask to handle data and image processing logic.
* **Database Management CLI:** A command-line tool (`manage.py`) for database operations (create tables, add/list/update/delete items).

## Tech Stack

* **Frontend:**
  * React
  * JavaScript (ES6+)
  * CSS3
  * `fetch` API for HTTP requests
* **Backend:**
  * Flask (Python)
  * PostgreSQL (Database)
  * SQLAlchemy (ORM)
  * Pillow (PIL Fork for image inspection)
  * `python-dotenv` (for environment variables)
  * `Flask-CORS`
  * `Flask-SQLAlchemy`
  * `psycopg2-binary` (PostgreSQL adapter)
  * `Click` (for `manage.py` CLI)
* **Development Tools:**
  * Node.js & npm (for frontend)
  * Python & pip (for backend)
  * Virtual Environments (for backend Python dependencies)

## Project Structure

```
d:\App\
├── backend\
│   ├── .env.example         # Example environment variables for backend
│   ├── .gitignore
│   ├── app.py               # Main Flask application
│   ├── manage.py            # CLI for database management
│   ├── requirements.txt     # Backend Python dependencies
│   ├── API_DOCUMENTATION.md # API endpoint details
│   ├── logs\                # Log files (generated, gitignored)
│   └── uploads\             # Uploaded user images (generated, gitignored)
├── frontend\
│   ├── .gitignore
│   ├── package.json
│   ├── public\
│   └── src\                 # React application source code
│       ├── App.jsx
│       ├── App.css
│       ├── main.jsx
│       └── components\
├── .gitignore               # Root gitignore
├── README.md                # This file
└── Pre-Production-Sec-Checklist.md # Security checklist
```

## Prerequisites

* **Node.js and npm:** For the frontend (Download from [nodejs.org](https://nodejs.org/))
* **Python 3.8+ and pip:** For the backend (Download from [python.org](https://python.org/))
* **PostgreSQL Server:** A running PostgreSQL instance. (Download from [postgresql.org](https://www.postgresql.org/download/))
* **Git:** For version control (Download from [git-scm.com](https://git-scm.com/))

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd App
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

* Copy `.env.example` to `.env`:

    ```bash
    # Windows
    copy .env.example .env

    # macOS/Linux
    cp .env.example .env
    ```

* Edit the `.env` file and set your `DATABASE_URL` and `FLASK_SECRET_KEY`.
    Example `DATABASE_URL`: `postgresql://user:password@host:port/database_name`
    Generate `FLASK_SECRET_KEY` using `python -c "import os; print(os.urandom(24).hex())"`

Create database tables using the management CLI:

```bash
python manage.py create-tables
```

You can also use `manage.py` to add initial data (see "Running `manage.py`" below).

### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install Node.js dependencies:

```bash
npm install
```

## Running the Application

You need to run both the backend and frontend servers.

### 1. Run the Backend Server

Ensure you are in the `backend` directory and your virtual environment is activated.

For development (using Flask's built-in server):

```bash
flask run
# By default, this runs on http://127.0.0.1:5000
```

Or, for a more production-like setup locally using Waitress (Windows/Cross-platform):

```bash
waitress-serve --host 127.0.0.1 --port 5000 app:app
```

(Ensure Waitress is installed: `pip install waitress`)

The backend API will be available at `http://127.0.0.1:5000`.

### 2. Run the Frontend Server

Ensure you are in the `frontend` directory.

```bash
npm run dev
```

This will typically start the React development server, and it will open the application in your web browser (usually at `http://localhost:5173` or a similar port).

## Running `manage.py` (Backend Database CLI)

The `manage.py` script in the `backend` directory provides commands for database management.
Ensure you are in the `backend` directory and your virtual environment is activated.

* **View available commands:**

    ```bash
    python manage.py --help
    ```

* **Create database tables:**

    ```bash
    python manage.py create-tables
    ```

* **Add a new item (prompts for details):**

    ```bash
    python manage.py add-item
    ```

* **List items:**

    ```bash
    python manage.py list-items
    python manage.py list-items --brand "YourBrandName"
    ```

* **Update an item (prompts for ID and fields):**

    ```bash
    python manage.py update-item
    ```

* **Delete an item (prompts for ID, requires confirmation):**

    ```bash
    python manage.py delete-item --confirm
    ```

* **Drop all tables (DANGEROUS! Requires confirmation):**

    ```bash
    python manage.py drop-tables --confirm
    ```

## API Documentation

Detailed information about the backend API endpoints, request/response formats, and status codes can be found in:
[`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md)

## Security Checklist

Before deploying this application to a production environment, please review the security checklist:
[`Pre-Production-Sec-Checklist.md`](Pre-Production-Sec-Checklist.md)

## Future Enhancements (Potential)

* Implement actual image processing for virtual try-on instead of simulation.
* User accounts and authentication.
* Saving try-on results.
* More advanced catalog filtering and searching.
* Admin panel for managing catalog items.
* Containerization with Docker.

---

This `README.md` provides a good overview for anyone looking to understand, set up, and run your project.

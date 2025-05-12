# Virtual Try-On Web Application

A modern web app for virtual clothing try-on. Users upload their photo and preview catalog items on themselves. Built with a React frontend and a Python Flask backend using a serverless SQLite database.

---

## Features

- **User Image Upload:** Upload your photo for virtual try-on.
- **Clothing Catalog:** Browse and filter by brand.
- **Virtual Try-On:** See a simulated preview of clothing on your photo.
- **Modern UI:** Responsive, brand-inspired design with smooth animations.
- **Admin Panel:** Web-based management of catalog via Flask-Admin.
- **Database Management CLI:** `manage.py` for advanced DB operations.

## Tech Stack

- **Frontend:** React, CSS3, Vite
- **Backend:** Flask, Flask-Admin, Flask-SQLAlchemy, Pillow, SQLite
- **Dev Tools:** Node.js, npm, Python 3.8+, pip, virtualenv, Git

## Project Structure

```
virtual-try-on-app/
├── backend/
│   ├── app.py              # Main Flask app (API + Admin)
│   ├── manage.py           # CLI for DB management
│   ├── requirements.txt    # Backend dependencies
│   ├── database.sqlite     # SQLite DB (auto-generated)
│   ├── init_db.py          # DB seeding script
│   ├── uploads/            # Uploaded user images
│   ├── logs/               # Log files
│   └── ...
├── frontend/
│   ├── src/                # React app source
│   ├── public/
│   ├── index.html
│   └── ...
├── README.md               # Project documentation
└── ...
```

## Prerequisites

- **Node.js & npm** (for frontend)
- **Python 3.8+ & pip** (for backend)
- **Git**

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/h3x0r-official/virtual-try-on-app.git
cd virtual-try-on-app
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python init_db.py        # Creates SQLite DB and seeds sample data
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

## Running the Application

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate
python app.py
# Flask API: http://127.0.0.1:5000
# Admin Panel: http://127.0.0.1:5000/admin
```

### 2. Start the Frontend

```bash
cd frontend
npm run dev
# App: http://localhost:5173
```

## Database Management

- Use the web admin at `/admin` for catalog CRUD.
- For advanced DB ops:

```bash
cd backend
source venv/bin/activate
python manage.py --help
```

## Cleaning Up

- Uploaded images: `backend/uploads/`
- Logs: `backend/logs/`
- SQLite DB: `backend/database.sqlite`

---

## License

MIT

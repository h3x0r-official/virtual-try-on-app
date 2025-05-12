# Database Integration Guide for Virtual Try-On Application

## Table of Contents

1. [Database Setup](#database-setup)
2. [Database Schema](#database-schema)
3. [Environment Configuration](#environment-configuration)
4. [Database Connection](#database-connection)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting](#troubleshooting)

## Database Setup

### Prerequisites

- PostgreSQL 12 or higher
- Python 3.8 or higher
- psycopg2-binary package

### Installation Steps

1. Install PostgreSQL:

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# For Fedora
sudo dnf install postgresql postgresql-server
```

2.Start PostgreSQL service:

```bash
# For Ubuntu/Debian
sudo service postgresql start

# For Fedora
sudo systemctl start postgresql
```

3.Create Database and User:

```bash
# Access PostgreSQL as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE tryon_db;
CREATE USER vapp WITH PASSWORD 'vapp';
ALTER DATABASE tryon_db OWNER TO vapp;
GRANT ALL PRIVILEGES ON DATABASE tryon_db TO vapp;
```

## Database Schema

The application uses the following database schema:

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Catalog Items Table

```sql
CREATE TABLE catalog_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Try-On Sessions Table

```sql
CREATE TABLE tryon_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    item_id INTEGER REFERENCES catalog_items(id),
    user_image_path VARCHAR(255) NOT NULL,
    result_image_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Configuration

Create a `.env` file in the backend directory with the following configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://vapp:vapp@localhost:5432/tryon_db

# Flask Configuration
FLASK_SECRET_KEY=your_secure_secret_key_here
FLASK_ENV=development

# File Upload Configuration
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif
```

## Database Connection

The application uses SQLAlchemy for database operations. The connection is configured in `backend/app.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
```

## API Endpoints

### Catalog Management

- `GET /api/catalog` - Get all catalog items
- `GET /api/catalog?brand=<brand_name>` - Get items by brand
- `POST /api/catalog` - Add new catalog item
- `GET /api/brands` - Get all available brands

### Try-On Operations

- `POST /api/upload` - Upload user image
- `POST /api/tryon` - Generate try-on result
- `GET /api/tryon/<session_id>` - Get try-on session status

## Troubleshooting

### Common Issues and Solutions

1. **Database Connection Error**
   - Verify PostgreSQL service is running
   - Check database credentials in `.env` file
   - Ensure database and user exist

2. **Permission Denied**
   - Verify user permissions:

   ```sql
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vapp;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vapp;
   ```

3. **Table Creation Issues**
   - Run database migrations:

   ```bash
   cd backend
   source venv/bin/activate
   python manage.py create-tables
   ```

4. **Data Insertion Problems**
   - Check table constraints
   - Verify data types match schema
   - Ensure required fields are provided

### Database Maintenance

1. **Backup Database**

```bash
pg_dump -U vapp tryon_db > backup.sql
```

2.**Restore Database**

```bash
psql -U vapp tryon_db < backup.sql
```

3.**Reset Database**

```bash
dropdb -U vapp tryon_db
createdb -U vapp tryon_db
python manage.py create-tables
```

## Security Best Practices

1. **Password Management**
   - Use strong, unique passwords
   - Store passwords securely using hashing
   - Never commit credentials to version control

2. **Connection Security**
   - Use SSL for database connections in production
   - Restrict database access to application servers
   - Use connection pooling for better performance

3. **Data Protection**
   - Implement proper input validation
   - Use parameterized queries to prevent SQL injection
   - Regular security audits and updates

## Performance Optimization

1. **Indexing**
   - Add indexes on frequently queried columns
   - Monitor query performance
   - Regular database maintenance

2. **Connection Pooling**
   - Configure appropriate pool size
   - Monitor connection usage
   - Implement connection timeout

3. **Query Optimization**
   - Use appropriate data types
   - Implement efficient joins
   - Regular query analysis and optimization

## Monitoring and Maintenance

1. **Regular Tasks**
   - Monitor database size
   - Check for long-running queries
   - Review error logs
   - Backup data regularly

2. **Performance Metrics**
   - Query execution time
   - Connection pool usage
   - Disk space usage
   - Cache hit ratio

## Support and Resources

- PostgreSQL Documentation: <https://www.postgresql.org/docs/>
- SQLAlchemy Documentation: <https://docs.sqlalchemy.org/>
- Flask-SQLAlchemy Documentation: <https://flask-sqlalchemy.palletsprojects.com/>

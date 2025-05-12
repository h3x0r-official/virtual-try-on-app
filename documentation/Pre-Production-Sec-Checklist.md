# Production Security Checklist - Virtual Try-On App

This document outlines critical security considerations and actions to take before deploying the Virtual Try-On application to a production environment.

## 1. Environment Configuration & Secrets Management

* **[ ] `.env` Files:**
  * Ensure `.env` files are **never** committed to version control (verify [`.gitignore`](.gitignore )).
  * Use separate `.env` files for development and production environments.
  * Production `.env` file must be securely managed on the production server.
* **[ ] Secret Keys & Credentials:**
  * **Flask `SECRET_KEY`:** Generate a strong, unique, random string for `FLASK_SECRET_KEY` in the production `.env`. Do not use the development key.
  * **Database Password:** Ensure the `DATABASE_URL` in the production `.env` uses a strong, unique password for the PostgreSQL user.
  * **`MANAGE_PASSWORD` (if re-enabled):** If authentication is added back to `manage.py`, ensure `MANAGE_PASSWORD` is strong and unique.
  * **Other API Keys/Secrets:** If any third-party services are integrated later, their API keys must be stored securely as environment variables and not hardcoded.
* **[ ] Environment-Specific Settings:**
  * Verify all environment variables (`DATABASE_URL`, `UPLOAD_FOLDER` paths, `FRONTEND_PRODUCTION_URL`, etc.) are correctly configured for the production environment.

## 2. Flask Application Security (Backend)

* **[ ] Debug Mode:**
  * Ensure Flask debug mode is **OFF** in production. (Set `FLASK_ENV=production` or `FLASK_DEBUG=0` environment variables, or rely on WSGI server defaults).
* **[ ] Input Validation:**
  * **API Endpoints:** Rigorously validate all incoming data (request bodies, query parameters, headers) for type, format, length, and allowed characters.
    * `/api/upload`: Validate file type, size, and potentially content.
    * `/api/tryon`: Validate `userImageFilename` and `clothingItemId` format/existence.
    * `/api/catalog`: Validate `brand` query parameter.
  * Use libraries like Marshmallow or Pydantic for robust schema validation if complexity grows.
* **[ ] Error Handling:**
  * Return generic error messages to the client for 5xx errors.
  * Log detailed error information (including stack traces) on the server-side only (current logging setup helps here).
* **[ ] CORS Configuration:**
  * Restrict `CORS` origins to the specific production frontend domain (`FRONTEND_PRODUCTION_URL`). Avoid wildcard `*` origins.
* **[ ] HTTPS:**
  * Ensure the application is served exclusively over HTTPS in production. This is typically handled by a reverse proxy (Nginx, Caddy).
* **[ ] Dependencies:**
  * Regularly update all Python dependencies (`requirements.txt`) to their latest stable and secure versions.
  * Periodically audit dependencies for known vulnerabilities (e.g., using `pip-audit` or GitHub Dependabot).
* **[ ] Rate Limiting:**
  * Implement rate limiting on sensitive or computationally expensive API endpoints (e.g., `/api/upload`, `/api/tryon`) to prevent abuse (e.g., using `Flask-Limiter`).
* **[ ] Security Headers:**
  * Configure the web server or Flask middleware to send security-enhancing HTTP headers:
    * `X-Content-Type-Options: nosniff`
    * `X-Frame-Options: DENY` (or `SAMEORIGIN` if embedding is needed)
    * `Content-Security-Policy (CSP)`: Define a strict CSP to mitigate XSS and other injection attacks.
    * `HTTP Strict Transport Security (HSTS)`: Enforce HTTPS.
    * `Referrer-Policy: strict-origin-when-cross-origin`

## 3. Database Security (PostgreSQL)

* **[ ] User Privileges:**
  * The PostgreSQL user configured in `DATABASE_URL` for the application should have the minimum necessary privileges (e.g., `SELECT`, `INSERT`, `UPDATE`, `DELETE` on specific tables, but not superuser rights or rights to modify schema arbitrarily after initial setup).
* **[ ] Network Access:**
  * Configure PostgreSQL to only accept connections from the application server's IP address. Avoid exposing the database directly to the public internet.
* **[ ] SQL Injection:**
  * Continue using SQLAlchemy ORM and parameterized queries. Avoid constructing SQL queries using string formatting with user input. Review any raw SQL queries if they are ever introduced.
* **[ ] Backups:**
  * Implement a regular, automated backup schedule for the production database.
  * Test the backup restoration process periodically.

## 4. File Upload Security (`/api/upload`)

* **[ ] File Type Validation:**
  * Strictly enforce `ALLOWED_EXTENSIONS`. Do not rely solely on client-side validation or `Content-Type` headers.
  * Consider using libraries that identify file types based on magic numbers (file signatures) in addition to extensions.
* **[ ] File Size Limits:**
  * Implement and enforce a reasonable maximum file size limit on the server-side (e.g., via Flask's `MAX_CONTENT_LENGTH` or in the WSGI/web server).
* **[ ] Filename Sanitization:**
  * Continue using `werkzeug.utils.secure_filename` to sanitize filenames.
* **[ ] Storage Location:**
  * **Ideal:** Store uploaded files outside the web application's root directory if possible (e.g., on a separate partition or cloud storage like S3).
  * If stored within the web root, ensure the `uploads` directory does not have script execution permissions.
* **[ ] Malware Scanning (Optional but Recommended):**
  * Consider integrating a malware scanner (e.g., ClamAV) to scan uploaded files, especially if they are user-generated content shared with others.
* **[ ] Serving Uploaded Files:**
  * If Flask serves files directly (`send_from_directory`):
    * Ensure this endpoint is protected if files are not meant to be public.
    * Set appropriate `Content-Disposition` headers (e.g., `inline` vs. `attachment`).
  * **Recommended for Production:** Use a dedicated web server (Nginx, Caddy) or a CDN to serve static/uploaded files for better performance and security.

## 5. Frontend Security (React)

* **[ ] Cross-Site Scripting (XSS):**
  * React automatically escapes data rendered in JSX, which helps prevent XSS.
  * Be extremely cautious if using `dangerouslySetInnerHTML`. Ensure any HTML passed to it is rigorously sanitized.
* **[ ] API Communication:**
  * Ensure all API calls are made over HTTPS to the backend.
* **[ ] Client-Side Secrets:**
  * Avoid storing any sensitive API keys or secrets directly in the frontend JavaScript code. If needed, use a backend proxy.
* **[ ] Dependencies:**
  * Regularly update frontend dependencies (`package.json`) using `npm update` or `yarn upgrade`.
  * Use `npm audit` or `yarn audit` to check for known vulnerabilities.

## 6. `manage.py` CLI Tool Security

* **[ ] Server Access Control:**
  * Ensure that access to the server where `manage.py` can be run is strictly controlled. Only authorized administrators should have shell access.
* **[ ] Command Sensitivity:**
  * Review commands like `drop-tables`. The `--confirm` flag is good. If this tool is used in a shared environment or by multiple people, re-evaluate the need for authentication for destructive commands.

## 7. Logging and Monitoring

* **[ ] Log Review:**
  * Ensure production logs (`backend/logs/backend.log`) are regularly reviewed for suspicious activity, errors, and security events.
  * Consider centralized logging solutions for easier management and analysis (e.g., ELK stack, Grafana Loki, cloud provider logging services).
* **[ ] Sensitive Data in Logs:**
  * Ensure no sensitive user data (passwords, raw API keys, excessive PII) is logged in plain text.
* **[ ] Monitoring:**
  * Set up monitoring for application performance, server resource usage, and error rates.

## 8. Deployment & Infrastructure

* **[ ] WSGI Server:**
  * Use a production-grade WSGI server (Gunicorn, Waitress) instead of the Flask development server.
* **[ ] Web Server (Reverse Proxy):**
  * Deploy a web server like Nginx or Caddy in front of the WSGI server to handle:
    * SSL/TLS termination (HTTPS).
    * Serving static and uploaded files.
    * Load balancing (if scaling).
    * Request buffering and basic security filtering.
* **[ ] Firewall:**
  * Configure server firewall (e.g., `ufw`, `firewalld`, cloud provider firewall) to only allow traffic on necessary ports (e.g., 80 for HTTP redirect, 443 for HTTPS).
* **[ ] System Patching:**
  * Keep the server's operating system and all installed software packages regularly patched and updated.

## 9. General Practices

* **[ ] Principle of Least Privilege:**
  * Apply this principle to all components: database users, application processes, file permissions, API access.
* **[ ] Code Reviews:**
  * Conduct code reviews with a focus on security implications before deploying new features.
* **[ ] Security Testing (Optional for current scale, good for future):**
  * Consider periodic vulnerability scanning or penetration testing as the application grows in complexity and user base.

This checklist provides a starting point. Security is an ongoing process, not a one-time task. Revisit and update this list as your application evolves.

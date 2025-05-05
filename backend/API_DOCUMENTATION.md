# Virtual Try-On API Documentation

This document describes the API endpoints for the Virtual Try-On backend application.

## Base URL

The API is served from the root of the Flask application (e.g., `http://127.0.0.1:5000`). All endpoints listed below are relative to this base URL.

---

## Endpoints

### 1. Health Check

* **Endpoint:** `/api/hello`
* **Method:** `GET`
* **Description:** Returns a simple hello message to confirm the backend is running and reachable.
* **Request:** None
* **Response:**
  * **Success (200 OK):**

        ```json
        {
          "message": "Hello from Flask Backend!"
        }
        ```

### 2. Get Available Brands

* **Endpoint:** `/api/brands`
* **Method:** `GET`
* **Description:** Retrieves a unique, alphabetically sorted list of all non-null brand names present in the clothing catalog.
* **Request:** None
* **Response:**
  * **Success (200 OK):** A JSON array of strings, each representing a unique brand name.

        ```json
        [
          "Breakout",
          "Edenrobe Men",
          "Outfitters"
        ]
        ```

  * **Error (500 Internal Server Error):** Indicates a problem fetching data from the database.

        ```json
        {
          "error": "Could not fetch brands"
        }
        ```

### 3. Get Clothing Catalog

* **Endpoint:** `/api/catalog`
* **Method:** `GET`
* **Description:** Retrieves a list of available clothing items. Can be filtered by brand.
* **Request:**
  * **Query Parameters (Optional):**
    * `brand` (string): If provided, filters the results to only include items matching the specified brand name (case-sensitive). Example: `/api/catalog?brand=Breakout`
* **Response:**
  * **Success (200 OK):** An array of clothing item objects (filtered or unfiltered).

        ```json
        [
          {
            "id": 1,
            "name": "Classic Blue Kurta",
            "price": 2500.00,
            "imageUrl": "http://example.com/images/kurta1.jpg",
            "brand": "Breakout"
          }
          // ... potentially more items
        ]
        ```

        *Note: `imageUrl` can be a string or `null`. `brand` field is now included.*
  * **Error (500 Internal Server Error):** Indicates a problem fetching data from the database.

        ```json
        {
          "error": "Could not fetch catalog"
        }
        ```

### 4. Upload User Image

* **Endpoint:** `/api/upload`
* **Method:** `POST`
* **Description:** Uploads a user's image file. In the current implementation, the file is validated and saved locally to the server's `uploads/` directory.
* **Request:**
  * **Content-Type:** `multipart/form-data`
  * **Body:** Must contain a file input field named `user_image`.
* **Response:**
  * **Success (200 OK):** Indicates the file was received and saved successfully.

        ```json
        {
          "message": "File '<filename>' uploaded successfully.",
          "filename": "<filename>"
        }
        ```

        *`<filename>` is the sanitized name of the file saved on the server.*
  * **Error (400 Bad Request):** Indicates a client-side error with the request.
    * If the `user_image` part is missing:

            ```json
            { "error": "No file part in the request" }
            ```

    * If no file was selected in the form:

            ```json
            { "error": "No selected file" }
            ```

    * If the file type is not allowed (e.g., not png, jpg, jpeg, gif):

            ```json
            { "error": "File type not allowed" }
            ```

  * **Error (500 Internal Server Error):** Indicates a problem saving the file on the server.

        ```json
        { "error": "Failed to save file on server" }
        ```

---

### Add Documentation for New Endpoints

(Add documentation for new endpoints here as they are created)

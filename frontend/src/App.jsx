import { useState, useEffect } from 'react';
import './App.css'; // Make sure this line imports the updated CSS

function App() {
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null); // State for image preview URL
  const [uploadStatus, setUploadStatus] = useState(''); // State for upload feedback
  const [isUploading, setIsUploading] = useState(false); // State to disable button during upload

  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://127.0.0.1:5000/api/catalog');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched Catalog Data:", data);
        setCatalog(data);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching catalog:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCatalog();
  }, []);

  // Update handler to create preview URL
  const handleFileChange = (event) => {
    setUploadStatus(''); // Clear previous status on new file selection
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];

      // Basic validation (Example: check if it's an image)
      if (!file.type.startsWith('image/')) {
        setUploadStatus('Error: Please select an image file.');
        setSelectedFile(null);
        setPreviewUrl(null);
        return; // Stop processing if not an image
      }

      console.log("Selected file:", file.name);
      setSelectedFile(file);

      // Create a URL for preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);

    } else {
      setSelectedFile(null);
      setPreviewUrl(null); // Clear preview if no file is selected
    }
  };

  // Function to handle the actual upload to the backend
  const handleImageUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }

    setIsUploading(true); // Disable button
    setUploadStatus('Uploading...');
    const formData = new FormData();
    // 'user_image' is the key the backend will expect
    formData.append('user_image', selectedFile);

    try {
      // Ensure this URL matches your backend endpoint
      const response = await fetch('http://127.0.0.1:5000/api/upload', {
        method: 'POST',
        body: formData,
        // No 'Content-Type' header needed for FormData with fetch
      });

      const result = await response.json(); // Always try to parse JSON

      if (!response.ok) {
        // Use error message from backend if available, otherwise use status text
        throw new Error(result.error || `Upload failed: ${response.status} ${response.statusText}`);
      }

      console.log('Upload successful:', result);
      setUploadStatus(`Upload successful! ${result.message || ''}`);
      // Potential next step: Store the returned image identifier/URL from 'result'
      // e.g., setUploadedImageUrl(result.imageUrl);

    } catch (err) {
      console.error('Error uploading image:', err);
      setUploadStatus(`Error: ${err.message}`);
    } finally {
      setIsUploading(false); // Re-enable button
    }
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>Virtual Try-On</h1>
      </header>

      {/* Main content area */}
      <div className="main-content">
        {/* Left Column: Upload and Preview */}
        <section className="user-section">
          <h2>Upload Your Photo</h2>
          <div className="upload-controls">
            <label htmlFor="file-upload" className="custom-file-upload">
              Browse...
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*" // Only allow image files
              onChange={handleFileChange}
              disabled={isUploading} // Disable input during upload
            />
            {selectedFile && <span className="file-name">{selectedFile.name}</span>}
          </div>
          {previewUrl && (
            <div className="image-preview">
              {/* Removed <h3>Preview:</h3> for cleaner look */}
              <img src={previewUrl} alt="Selected preview" />
            </div>
          )}

          {/* Upload Button - appears only when a file is selected */}
          {selectedFile && (
            <button
              onClick={handleImageUpload}
              className="upload-button"
              disabled={isUploading} // Disable button while uploading
              style={{ marginTop: '15px' }}
            >
              {isUploading ? 'Uploading...' : 'Upload Image'}
            </button>
          )}

          {/* Upload Status Message */}
          {uploadStatus && (
            <p className="upload-status" style={{ marginTop: '10px' }}>
              {uploadStatus}
            </p>
          )}

        </section>

        {/* Right Column: Catalog */}
        <section className="catalog-section">
          <h2>Clothing Catalog</h2>
          {loading && <p>Loading catalog...</p>}
          {error && <p className="error-message">Error loading catalog: {error}</p>}
          {!loading && !error && (
            <div className="catalog-list">
              {catalog.length > 0 ? (
                catalog.map(item => (
                  <div key={item.id} className="catalog-item">
                    {/* Check if imageUrl exists before rendering the image */}
                    {item.imageUrl ? (
                      <img
                        src={item.imageUrl}
                        alt={item.name} // Add alt text for accessibility
                        className="item-image" // Add a class for potential styling
                      />
                    ) : (
                      // Fallback if no imageUrl is provided
                      <div className="item-image-placeholder">
                        <span>Image Not Available</span>
                      </div>
                    )}
                    <div className="item-details">
                      <h3>{item.name}</h3>
                      <p>PKR {item.price}</p>
                      {/* Add Try On Button Here Later */}
                    </div>
                  </div>
                ))
              ) : (
                <p>No items found in the catalog.</p>
              )}
            </div>
          )}
        </section>
      </div>
      {/* Potential Footer could go here */}
    </div>
  );
}

export default App;
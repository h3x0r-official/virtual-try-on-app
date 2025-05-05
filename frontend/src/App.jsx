import { useState, useEffect } from 'react';
import './App.css'; // Make sure this line imports the updated CSS

function App() {
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null); // State for image preview URL

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
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
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
              accept="image/*"
              onChange={handleFileChange}
            />
            {selectedFile && <span className="file-name">{selectedFile.name}</span>}
          </div>
          {previewUrl && (
            <div className="image-preview">
              <h3>Preview:</h3>
              <img src={previewUrl} alt="Selected preview" style={{ maxWidth: '100%', height: 'auto', marginTop: '10px' }} />
            </div>
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
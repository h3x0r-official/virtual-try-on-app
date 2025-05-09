import { useState, useEffect } from 'react';
import Navbar from './components/Navbar'; // Import the Navbar component
import CatalogItemCard from './components/CatalogItemCard'; // Import the new component
import './App.css';

// Define constant for the "All Brands" option, matching Navbar.jsx
const ALL_BRANDS_OPTION = "All Brands";

function App() {
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  // State for the currently selected brand filter
  const [selectedBrand, setSelectedBrand] = useState(ALL_BRANDS_OPTION); // Default to 'All Brands'
  // Add state for the item selected for try-on
  const [selectedTryOnItem, setSelectedTryOnItem] = useState(null);

  // --- New State for Try-On Process ---
  const [uploadedFilename, setUploadedFilename] = useState(null); // Store filename from upload response
  const [tryOnResultUrl, setTryOnResultUrl] = useState(null); // Store the result image URL
  const [isGeneratingTryOn, setIsGeneratingTryOn] = useState(false); // Loading state for try-on API call
  const [tryOnError, setTryOnError] = useState(null); // Error state for try-on API call

  // Effect to fetch catalog based on the selected brand
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        setLoading(true);
        setError(null); // Clear previous errors

        // Construct the URL based on the selected brand
        let fetchUrl = 'http://127.0.0.1:5000/api/catalog';
        if (selectedBrand !== ALL_BRANDS_OPTION) {
          // Append the brand query parameter if a specific brand is selected
          fetchUrl += `?brand=${encodeURIComponent(selectedBrand)}`;
        }

        console.log(`Fetching catalog from: ${fetchUrl}`); // Log the URL being fetched

        const response = await fetch(fetchUrl);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(`Fetched Catalog Data for ${selectedBrand}:`, data);
        setCatalog(data);
      } catch (err) {
        setError(`Failed to load catalog: ${err.message}`);
        console.error(`Error fetching catalog for ${selectedBrand}:`, err);
        setCatalog([]); // Clear catalog on error
      } finally {
        setLoading(false);
      }
    };

    fetchCatalog();
  }, [selectedBrand]); // Re-run this effect whenever selectedBrand changes

  // Handler function to update the selected brand state
  const handleBrandSelect = (brand) => {
    console.log("Brand selected:", brand);
    setSelectedBrand(brand);
    setSelectedTryOnItem(null); // Clear try-on selection when changing brand
    // Optional: Reset upload state when changing brand
    // setSelectedFile(null);
    // setPreviewUrl(null);
    // setUploadStatus('');
  };

  // Update handler to create preview URL
  const handleFileChange = (event) => {
    setUploadStatus(''); // Clear previous status on new file selection
    setUploadedFilename(null); // Clear previous upload filename
    setTryOnResultUrl(null); // Clear previous result
    setTryOnError(null); // Clear previous try-on error
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
    setUploadedFilename(null); // Clear previous filename
    setTryOnResultUrl(null); // Clear previous result
    setTryOnError(null); // Clear previous try-on error
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
      setUploadStatus(`Upload successful! Ready for Try-On.`);
      setUploadedFilename(result.filename); // <-- Store the filename
      // Potential next step: Store the returned image identifier/URL from 'result'
      // e.g., setUploadedImageUrl(result.imageUrl);

    } catch (err) {
      console.error('Error uploading image:', err);
      setUploadStatus(`Error: ${err.message}`);
      setUploadedFilename(null); // Ensure filename is null on error
    } finally {
      setIsUploading(false); // Re-enable button
    }
  };

  // Handler for when a "Try On" button is clicked on a card
  const handleTryOnSelect = (item) => {
    // Optional: Toggle selection - if clicking the already selected item, deselect it.
    if (selectedTryOnItem && selectedTryOnItem.id === item.id) {
      console.log("Deselected item for Try On:", item);
      setSelectedTryOnItem(null);
      setTryOnResultUrl(null); // Clear result if item deselected
      setTryOnError(null);
    } else {
      console.log("Selected item for Try On:", item);
      setSelectedTryOnItem(item);
      setTryOnResultUrl(null); // Clear previous result when selecting new item
      setTryOnError(null);
    }
  };

  // --- New Handler for Generating Try-On ---
  const handleGenerateTryOn = async () => {
    if (!uploadedFilename || !selectedTryOnItem) {
      setTryOnError("Please upload your photo and select a clothing item first.");
      return;
    }

    setIsGeneratingTryOn(true);
    setTryOnError(null);
    setTryOnResultUrl(null); // Clear previous result

    console.log(`Requesting Try-On: User Image='${uploadedFilename}', Item ID=${selectedTryOnItem.id}`);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/tryon', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userImageFilename: uploadedFilename,
          clothingItemId: selectedTryOnItem.id,
        }),
      });

      const result = await response.json(); // Always try to parse JSON

      if (!response.ok) {
        // Use error message from backend if available
        throw new Error(result.error || `Try-On failed: ${response.status} ${response.statusText}`);
      }

      console.log('Try-On successful (simulated):', result);
      setTryOnResultUrl(result.resultImageUrl); // Store the result URL

    } catch (err) {
      console.error('Error generating try-on:', err);
      setTryOnError(`Try-On Error: ${err.message}`);
      setTryOnResultUrl(null); // Ensure result is null on error
    } finally {
      setIsGeneratingTryOn(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Virtual Try-On</h1>
      </header>

      {/* Render the Navbar component */}
      <Navbar
        selectedBrand={selectedBrand}
        onBrandSelect={handleBrandSelect}
      />

      {/* Main content area */}
      <div className="main-content">
        {/* Left Column: Upload and Preview */}
        <section className="user-section">
          <h2>Your Photo & Try-On</h2> {/* Updated Title */}
          <div className="upload-controls">
            <label htmlFor="file-upload" className="custom-file-upload">
              Browse...
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*" // Only allow image files
              onChange={handleFileChange}
              disabled={isUploading || isGeneratingTryOn} // Disable input during upload
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
          {selectedFile && !uploadedFilename && ( // Show only if file selected but not yet successfully uploaded
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

          {/* Display which item is selected for try-on (optional feedback) */}
          {selectedTryOnItem && (
            <p className="try-on-selection-info">
              Selected: <strong>{selectedTryOnItem.name}</strong>
            </p>
          )}

          {/* Generate Try-On Button */}
          <button
            onClick={handleGenerateTryOn}
            className="generate-tryon-button" // New class for styling
            disabled={!uploadedFilename || !selectedTryOnItem || isGeneratingTryOn || isUploading}
          >
            {isGeneratingTryOn ? 'Generating...' : 'Generate Try-On'}
          </button>

          {/* Try-On Error Message & Spinner */}
          {tryOnError && <p className="error-message tryon-error">{tryOnError}</p>}

          {isGeneratingTryOn && <div className="spinner"></div>}

          {/* Try-On Result Display */}
          {isGeneratingTryOn && !tryOnError && tryOnResultUrl === null && uploadedFilename && selectedTryOnItem && (
            <p className="tryon-result-info">Try-on generated, but no result image available (item might be missing image).</p>
          )}
          {tryOnResultUrl && (
            <div className="tryon-result">
              <h3>Try-On Result (Simulated)</h3>
              <img src={tryOnResultUrl} alt="Simulated try-on result" />
            </div>
          )}

        </section>

        {/* Right Column: Catalog Slider */}
        <section className="catalog-section">
          <h2>{selectedBrand} Catalog</h2>
          {loading && <div className="spinner"></div>}
          {error && <p className="error-message">{error}</p>}
          {!loading && !error && (
            <div className="catalog-slider">
              {catalog.length > 0 ? (
                // Use the CatalogItemCard component here
                catalog.map(item => (
                  <CatalogItemCard
                    key={item.id}
                    item={item}
                    // Pass the handler function as a prop
                    onTryOnSelect={handleTryOnSelect}
                    // Pass down whether this item is the selected one
                    isSelected={selectedTryOnItem && selectedTryOnItem.id === item.id}
                  />
                ))
              ) : (
                <p>No items found for {selectedBrand}.</p>
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
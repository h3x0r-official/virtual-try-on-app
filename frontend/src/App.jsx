import { useState, useEffect } from 'react';
import './App.css'; // Make sure this line imports the updated CSS

function App() {
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Virtual Try-On</h1>
      </header>

      {/* Wrap main content area in the container */}
      <div className="container">
        <main className="App-main">
          <h2>Clothing Catalog</h2>
          {loading && <p>Loading catalog...</p>}
          {error && <p style={{ color: 'red' }}>Error loading catalog: {error}</p>}
          {!loading && !error && (
            <div className="catalog-list">
              {catalog.length > 0 ? (
                catalog.map(item => (
                  <div key={item.id} className="catalog-item">
                    <div className="item-image-placeholder">
                      {/* Actual <img> tag will replace this later */}
                    </div>
                    {/* Group text details */}
                    <div className="item-details">
                      <h3>{item.name}</h3>
                      <p>PKR {item.price}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p>No items found in the catalog.</p>
              )}
            </div>
          )}
        </main>
      </div>
      {/* Potential Footer could go here */}
    </div>
  );
}

export default App;
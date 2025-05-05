import React, { useState, useEffect } from 'react';
import './Navbar.css'; // We'll create this CSS file next

const ALL_BRANDS_OPTION = "All Brands"; // Define constant for clarity

function Navbar({ selectedBrand, onBrandSelect }) {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://127.0.0.1:5000/api/brands');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Add "All Brands" option to the beginning of the fetched list
        setBrands([ALL_BRANDS_OPTION, ...data]);
        console.log("Fetched Brands:", [ALL_BRANDS_OPTION, ...data]);
      } catch (err) {
        setError(`Failed to load brands: ${err.message}`);
        console.error("Error fetching brands:", err);
        setBrands([ALL_BRANDS_OPTION]); // Fallback to just "All Brands" on error
      } finally {
        setLoading(false);
      }
    };

    fetchBrands();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <nav className="brand-nav">
      {loading && <p>Loading brands...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && (
        <ul>
          {brands.map(brand => (
            <li key={brand}>
              <button
                onClick={() => onBrandSelect(brand)}
                className={selectedBrand === brand ? 'active' : ''}
              >
                {brand}
              </button>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}

export default Navbar;
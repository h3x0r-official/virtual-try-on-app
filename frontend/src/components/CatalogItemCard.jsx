import React from 'react';
import './CatalogItemCard.css';

// Accept onTryOnSelect prop
function CatalogItemCard({ item, onTryOnSelect }) {
  const { name, price, imageUrl, brand } = item;

  // Handler for the button click
  const handleTryOnClick = () => {
    // Call the function passed from the parent, providing the item data
    if (onTryOnSelect) {
      onTryOnSelect(item);
    }
  };

  return (
    <div className="catalog-item-card">
      {/* Image Section */}
      <div className="card-image-container">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={name} // Use item name for alt text
            className="card-image"
          />
        ) : (
          // Fallback if no imageUrl is provided
          <div className="card-image-placeholder">
            <span>Image Not Available</span>
          </div>
        )}
      </div>

      {/* Details Section */}
      <div className="card-details">
        <h3>{name}</h3>
        <p className="card-price">PKR {price.toFixed(2)}</p> {/* Format price */}
        {/* Display brand if available */}
        {brand && <p className="card-brand">{brand}</p>}
        {/* Add Try On Button */}
        <button className="try-on-button" onClick={handleTryOnClick}>
          Try On
        </button>
      </div>
    </div>
  );
}

export default CatalogItemCard;
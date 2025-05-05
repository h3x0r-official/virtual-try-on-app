import React from 'react';
import './CatalogItemCard.css'; // We'll create this CSS file next

// Destructure the item prop directly in the function signature
function CatalogItemCard({ item }) {
  // Destructure properties from the item object for easier access
  const { name, price, imageUrl, brand } = item;

  return (
    <div className="catalog-item-card"> {/* Use a specific class name */}
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
        {/* Placeholder for Try On Button - Add in the next step */}
        {/* <button className="try-on-button">Try On</button> */}
      </div>
    </div>
  );
}

export default CatalogItemCard;
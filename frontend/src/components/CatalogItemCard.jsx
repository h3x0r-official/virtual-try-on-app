import React from 'react';
import './CatalogItemCard.css';

// Accept isSelected prop
function CatalogItemCard({ item, onTryOnSelect, isSelected }) {
  const { name, price, imageUrl, brand } = item;

  const handleTryOnClick = () => {
    if (onTryOnSelect) {
      onTryOnSelect(item);
    }
  };

  // Determine the class name based on selection state
  const cardClassName = `catalog-item-card ${isSelected ? 'selected' : ''}`;

  return (
    // Use the dynamic class name
    <div className={cardClassName}>
      {/* Image Section */}
      <div className="card-image-container">
        {imageUrl ? (
          <img src={imageUrl} alt={name} className="card-image" />
        ) : (
          <div className="card-image-placeholder">
            <span>Image Not Available</span>
          </div>
        )}
      </div>

      {/* Details Section */}
      <div className="card-details">
        <h3>{name}</h3>
        <p className="card-price">PKR {price.toFixed(2)}</p>
        {brand && <p className="card-brand">{brand}</p>}
        <button className="try-on-button" onClick={handleTryOnClick}>
          {/* Change button text based on selection? (Optional) */}
          {isSelected ? 'Selected' : 'Try On'}
        </button>
      </div>
    </div>
  );
}

export default CatalogItemCard;
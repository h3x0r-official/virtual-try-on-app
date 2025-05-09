from app import app, db, ClothingItem
import os

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have data
        if ClothingItem.query.first() is None:
            # Add sample clothing items
            sample_items = [
                ClothingItem(
                    name="Classic White T-Shirt",
                    price=29.99,
                    imageUrl="https://example.com/white-tshirt.jpg",
                    brand="BasicWear"
                ),
                ClothingItem(
                    name="Slim Fit Jeans",
                    price=79.99,
                    imageUrl="https://example.com/slim-jeans.jpg",
                    brand="DenimCo"
                ),
                ClothingItem(
                    name="Casual Hoodie",
                    price=59.99,
                    imageUrl="https://example.com/hoodie.jpg",
                    brand="StreetStyle"
                ),
                ClothingItem(
                    name="Formal Dress Shirt",
                    price=89.99,
                    imageUrl="https://example.com/dress-shirt.jpg",
                    brand="Elegance"
                )
            ]
            
            # Add items to database
            for item in sample_items:
                db.session.add(item)
            
            # Commit the changes
            db.session.commit()
            print("Sample data added successfully!")
        else:
            print("Database already contains data. Skipping sample data insertion.")

if __name__ == "__main__":
    init_db() 
from app import db, Product, UserBehavior
import json
from datetime import datetime
import random
import uuid

def create_tables():
    """Create database tables"""
    db.create_all()
    print("Database tables created.")

def create_sample_data():
    """Create sample products and user data for testing"""
    
    # Sample products
    products_data = [
        {
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
            "category": "Electronics",
            "price": 199.99,
            "brand": "SoundMax",
            "image_url": "https://via.placeholder.com/300x200?text=Headphones",
            "features": json.dumps({"color": "Black", "battery": "30 hours", "connectivity": "Bluetooth 5.0"})
        },
        {
            "name": "Smart Fitness Watch",
            "description": "Advanced fitness tracking watch with heart rate monitor and GPS",
            "category": "Electronics",
            "price": 299.99,
            "brand": "FitTech",
            "image_url": "https://via.placeholder.com/300x200?text=Watch",
            "features": json.dumps({"waterproof": "Yes", "battery": "7 days", "sensors": "Heart rate, GPS"})
        },
        {
            "name": "Premium Smartphone",
            "description": "Latest smartphone with high-resolution camera and fast processor",
            "category": "Electronics",
            "price": 899.99,
            "brand": "TechPro",
            "image_url": "https://via.placeholder.com/300x200?text=Smartphone",
            "features": json.dumps({"storage": "256GB", "camera": "48MP", "screen": "6.5 inch OLED"})
        },
        {
            "name": "Ultrabook Laptop",
            "description": "Thin and light laptop with all-day battery life and powerful performance",
            "category": "Electronics",
            "price": 1299.99,
            "brand": "CompTech",
            "image_url": "https://via.placeholder.com/300x200?text=Laptop",
            "features": json.dumps({"processor": "Intel i7", "ram": "16GB", "storage": "512GB SSD"})
        }
    ]
    
    # Create products
    print("Creating products...")
    for product_data in products_data:
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            category=product_data["category"],
            price=product_data["price"],
            brand=product_data["brand"],
            image_url=product_data["image_url"],
            features=product_data["features"]
        )
        db.session.add(product)
    
    # Generate user behaviors
    print("Creating user behaviors...")
    session_ids = [str(uuid.uuid4()) for _ in range(3)]
    products = Product.query.all()
    
    for session_id in session_ids:
        for _ in range(random.randint(3, 8)):
            product = random.choice(products)
            behavior_type = random.choice(['view', 'purchase', 'add_to_cart'])
            
            behavior = UserBehavior(
                session_id=session_id,
                product_id=product.id,
                behavior_type=behavior_type
            )
            db.session.add(behavior)
    
    db.session.commit()
    print("Sample data created successfully.")

if __name__ == "__main__":
    create_tables()
    create_sample_data()

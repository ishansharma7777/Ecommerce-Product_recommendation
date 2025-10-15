import os
import json
from datetime import datetime, timedelta
import random
from supabase_rest import SupabaseClient

# Initialize Supabase client
supabase = SupabaseClient()

def create_sample_data():
    """Create sample products and user data for testing using Supabase REST API"""
    
    # Sample products
    products_data = [
        {
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
            "category": "Electronics",
            "price": 199.99,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300"
        },
        {
            "name": "Smart Fitness Watch",
            "description": "Advanced fitness tracking watch with heart rate monitor and GPS",
            "category": "Electronics",
            "price": 299.99,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300"
        },
        {
            "name": "Organic Cotton T-Shirt",
            "description": "Comfortable organic cotton t-shirt in various colors",
            "category": "Clothing",
            "price": 29.99,
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300"
        },
        {
            "name": "Stainless Steel Water Bottle",
            "description": "Insulated stainless steel water bottle that keeps drinks cold for 24 hours",
            "category": "Home & Kitchen",
            "price": 24.99,
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=300"
        },
        {
            "name": "Wireless Charging Pad",
            "description": "Fast wireless charging pad compatible with all Qi-enabled devices",
            "category": "Electronics",
            "price": 39.99,
            "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300"
        },
        {
            "name": "Yoga Mat Premium",
            "description": "Non-slip yoga mat with excellent grip and cushioning",
            "category": "Sports & Fitness",
            "price": 49.99,
            "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=300"
        },
        {
            "name": "Coffee Maker Deluxe",
            "description": "Programmable coffee maker with built-in grinder and thermal carafe",
            "category": "Home & Kitchen",
            "price": 149.99,
            "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300"
        },
        {
            "name": "Running Shoes Pro",
            "description": "Lightweight running shoes with responsive cushioning and breathable upper",
            "category": "Sports & Fitness",
            "price": 129.99,
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300"
        },
        {
            "name": "Laptop Stand Adjustable",
            "description": "Ergonomic laptop stand with adjustable height and angle",
            "category": "Electronics",
            "price": 59.99,
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300"
        },
        {
            "name": "Essential Oil Diffuser",
            "description": "Ultrasonic essential oil diffuser with LED lights and timer",
            "category": "Home & Kitchen",
            "price": 34.99,
            "image_url": "https://images.unsplash.com/photo-1607853202273-797f1c22a7e2?w=300"
        }
    ]
    
    # Create products
    print("Creating products...")
    for product_data in products_data:
        # Insert product using Supabase REST API
        result = supabase.insert('products', product_data)
        if result:
            print(f"Added product: {product_data['name']}")
        else:
            print(f"Failed to add product: {product_data['name']}")
    
    # Generate session IDs for user behaviors
    import uuid
    session_ids = [str(uuid.uuid4()) for _ in range(5)]
    
    # Get all products
    print("Fetching products...")
    products = supabase.select('products')
    if not products:
        print("Failed to fetch products")
        return
    
    # Create sample user behaviors
    print("Creating user behaviors...")
    behavior_types = ['view', 'like', 'cart', 'purchase']
    
    # Generate random behaviors for each session
    for session_id in session_ids:
        print(f"Creating behaviors for session: {session_id}")
        # Each session interacts with 3-8 products
        num_interactions = random.randint(3, min(8, len(products)))
        selected_products = random.sample(products, num_interactions)
        
        for product in selected_products:
            # Generate 1-3 behaviors per product
            num_product_behaviors = random.randint(1, 3)
            behavior_types_for_product = random.sample(behavior_types, num_product_behaviors)
            
            for behavior_type in behavior_types_for_product:
                # Random timestamp within last 30 days
                days_ago = random.randint(0, 30)
                timestamp = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
                
                behavior_data = {
                    "session_id": session_id,
                    "product_id": product['id'],
                    "behavior_type": behavior_type,
                    "timestamp": timestamp
                }
                
                # Insert behavior using Supabase REST API
                result = supabase.insert('user_behaviors', behavior_data)
                if result:
                    print(f"Added {behavior_type} behavior for product {product['id']}")
                else:
                    print(f"Failed to add behavior: {behavior_type} for product {product['id']}")
    
    # Create sample recommendations
    print("Creating recommendations...")
    for i in range(len(products)):
        source_product = products[i]
        # Generate 2-4 recommendations for each product
        num_recommendations = random.randint(2, 4)
        # Get random products excluding the source product
        other_products = [p for p in products if p['id'] != source_product['id']]
        recommended_products = random.sample(other_products, min(num_recommendations, len(other_products)))
        
        for recommended_product in recommended_products:
            recommendation_data = {
                "source_product_id": source_product['id'],
                "recommended_product_id": recommended_product['id'],
                "recommendation_score": round(random.uniform(0.5, 1.0), 2),
                "explanation": f"Products frequently bought together"
            }
            
            # Insert recommendation using Supabase REST API
            result = supabase.insert('recommendations', recommendation_data)
            if result:
                print(f"Added recommendation from product {source_product['id']} to {recommended_product['id']}")
            else:
                print(f"Failed to add recommendation from product {source_product['id']} to {recommended_product['id']}")
    
    print("Sample data created successfully!")

if __name__ == '__main__':
    # Test connection first
    if supabase.test_connection():
        create_sample_data()
    else:
        print("Failed to connect to Supabase. Please check your configuration.")

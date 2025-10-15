# 🎯 **Supabase Database Setup - Complete Guide**

## 📊 **Database Tables You Need to Create**

### **1. PRODUCTS Table (Product Catalog)**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2),
    brand VARCHAR(100),
    rating DECIMAL(3,2),
    image_url VARCHAR(500),
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Columns Explained:**
- `id`: Unique product identifier (auto-generated)
- `name`: Product name (required)
- `description`: Detailed product description
- `category`: Product category (Electronics, Clothing, etc.)
- `price`: Product price in decimal format
- `brand`: Brand name
- `rating`: Average customer rating (1-5)
- `image_url`: URL to product image
- `features`: JSON object with product features
- `created_at`: When product was added

### **2. USERS Table (User Information)**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Columns Explained:**
- `id`: Unique user identifier (auto-generated)
- `name`: User's full name (required)
- `email`: User's email address (unique, required)
- `preferences`: JSON object with user preferences
- `created_at`: When account was created

### **3. USER_INTERACTIONS Table (User Behavior)**
```sql
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    interaction_type VARCHAR(50) NOT NULL,
    rating INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

**Columns Explained:**
- `id`: Unique interaction identifier (auto-generated)
- `user_id`: Links to users table (foreign key)
- `product_id`: Links to products table (foreign key)
- `interaction_type`: Type of interaction (view, like, cart, purchase)
- `rating`: User rating (1-5) if applicable
- `timestamp`: When interaction happened

### **4. RECOMMENDATIONS Table (Generated Recommendations)**
```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    score DECIMAL(5,4),
    explanation TEXT,
    algorithm VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Columns Explained:**
- `id`: Unique recommendation identifier (auto-generated)
- `user_id`: Links to users table (foreign key)
- `product_id`: Links to products table (foreign key)
- `score`: Recommendation confidence score (0-1)
- `explanation`: AI-generated explanation text
- `algorithm`: Algorithm used (collaborative, content_based, hybrid)
- `created_at`: When recommendation was generated

---

## 🚀 **Quick Setup Steps**

### **Step 1: Create Supabase Project**
1. Go to https://supabase.com
2. Sign up/Sign in
3. Create new project: `ecommerce-recommender`
4. Save your database password!

### **Step 2: Get Connection String**
1. Go to **Settings** → **Database**
2. Copy the **URI** connection string
3. Format: `postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres`

### **Step 3: Setup Your Project**
```bash
# 1. Get connection string
./venv/bin/python get_supabase_connection.py

# 2. Setup database automatically
./venv/bin/python setup_supabase.py

# 3. Start application
./venv/bin/python app.py
```

---

## 📝 **Sample Data Structure**

### **Products (Your Product Catalog)**
```json
{
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "category": "Electronics",
  "price": 199.99,
  "brand": "TechSound",
  "rating": 4.5,
  "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
  "features": {
    "battery_life": "30 hours",
    "noise_cancellation": "Active",
    "connectivity": "Bluetooth 5.0"
  }
}
```

### **Users**
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "preferences": {
    "categories": ["Electronics", "Sports & Fitness"],
    "price_range": [50, 200],
    "brands": ["TechSound", "FitTech"]
  }
}
```

### **User Interactions (User Behavior)**
```json
{
  "user_id": 1,
  "product_id": 2,
  "interaction_type": "purchase",
  "rating": 5,
  "timestamp": "2025-10-12T14:30:00Z"
}
```

---

## 🔧 **Database Indexes for Performance**
```sql
-- Add these indexes for better performance
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_product_id ON user_interactions(product_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
```

---

## ✅ **What You Get**

After setup, you'll have:
- ✅ **Product Catalog**: Store all your products with features
- ✅ **User Management**: Track user information and preferences
- ✅ **Behavior Tracking**: Monitor user interactions (views, likes, purchases)
- ✅ **Recommendation Engine**: Generate personalized product suggestions
- ✅ **AI Explanations**: LLM-powered explanations for recommendations
- ✅ **Modern Frontend**: Beautiful React dashboard
- ✅ **RESTful API**: Complete API for all operations

---

## 🎯 **Key Features**

1. **Hybrid Recommendation Algorithm**: Combines collaborative and content-based filtering
2. **Real-time Recommendations**: Dynamic suggestions based on user behavior
3. **LLM Integration**: AI-generated explanations for each recommendation
4. **Scalable Database**: PostgreSQL with proper indexing
5. **Modern UI**: React frontend with Tailwind CSS
6. **Production Ready**: SSL support, connection pooling, error handling

Your Supabase database will be the perfect foundation for a scalable e-commerce recommendation system! 🚀

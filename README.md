# E-commerce Product Recommender

An intelligent e-commerce recommendation system that combines collaborative filtering, content-based filtering, and LLM-powered explanations to provide personalized product recommendations.

## 🎥 Demo Video

https://github.com/ishansharma7777/Ecommerce-Product_recommendation/blob/main/WhatsApp%20Video%202025-10-15%20at%2023.39.32.mp4

## Features

- **Hybrid Recommendation Engine**: Combines collaborative filtering and content-based filtering
- **LLM-Powered Explanations**: Uses OpenAI GPT to generate personalized explanations for each recommendation
- **Interactive Dashboard**: Modern React-based frontend for exploring recommendations
- **Multiple Algorithms**: Support for collaborative, content-based, and hybrid recommendation approaches
- **User Behavior Tracking**: Tracks user interactions (views, likes, cart additions, purchases)
- **Real-time Recommendations**: Dynamic recommendations based on user activity

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask API     │    │   SQLite DB     │
│                 │    │                 │    │                 │
│ • User Selection│◄──►│ • Recommendations│◄──►│ • Products      │
│ • Algorithm     │    │ • User Mgmt     │    │ • Users         │
│ • Dashboard     │    │ • LLM Integration│    │ • Interactions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │                 │
                       │ • GPT-3.5-turbo │
                       │ • Explanations  │
                       └─────────────────┘
```

## Prerequisites

- Python 3.8+
- External PostgreSQL database (Supabase, Railway, Neon, etc.)
- OpenAI API key (optional for LLM explanations)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-recommender
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Supabase database**
   ```bash
   # Get your Supabase connection string
   ./venv/bin/python get_supabase_connection.py
   
   # Setup database automatically
   ./venv/bin/python setup_supabase.py
   ```

4. **Start the application**
   ```bash
   ./venv/bin/python app.py
   ```

5. **Access the frontend**
   - Frontend: http://localhost:8001/frontend.html
   - API: http://localhost:5001/api

## Usage

### Backend API

The Flask API provides the following endpoints:

#### Products
- `GET /api/products` - Get all products

#### Users
- `POST /api/users` - Create a new user
- `GET /api/users/{user_id}/interactions` - Get user interactions
- `POST /api/users/{user_id}/interactions` - Add user interaction

#### Recommendations
- `GET /api/users/{user_id}/recommendations?algorithm={type}&n={count}` - Get recommendations

**Parameters:**
- `algorithm`: `collaborative`, `content`, or `hybrid` (default)
- `n`: Number of recommendations (default: 5)

### Frontend Dashboard

1. **Select a User**: Choose from the available users
2. **Choose Algorithm**: Select between collaborative, content-based, or hybrid filtering
3. **View Recommendations**: See personalized product recommendations with AI explanations
4. **Check Activity**: View user's recent interactions

## Recommendation Algorithms

### 1. Collaborative Filtering
- Finds users with similar interaction patterns
- Recommends products liked by similar users
- Uses weighted ratings based on interaction types

### 2. Content-Based Filtering
- Analyzes product features using TF-IDF vectorization
- Creates user profiles based on liked products
- Recommends products similar to user preferences

### 3. Hybrid Approach
- Combines collaborative and content-based scores
- Collaborative filtering: 60% weight
- Content-based filtering: 40% weight

## LLM Integration

The system uses OpenAI's GPT-3.5-turbo to generate personalized explanations:

**Example Prompt:**
```
Explain why the product "Wireless Bluetooth Headphones" ($199.99) is recommended to user "Alice Johnson" based on their behavior.

User's recent activity:
- purchased Smart Fitness Watch
- liked Yoga Mat Premium
- viewed Running Shoes Pro

Product details:
- Category: Electronics
- Brand: TechSound
- Description: High-quality wireless headphones...
- Rating: 4.5/5

Recommendation algorithm: hybrid
Recommendation score: 0.85
```

## Sample Data

The system includes sample data for testing:

- **10 Products**: Electronics, Clothing, Home & Kitchen, Sports & Fitness
- **5 Users**: With different preferences and interaction patterns
- **Random Interactions**: Views, likes, cart additions, and purchases

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for explanations)
- `FLASK_ENV`: Flask environment (development/production)
- `DATABASE_URL`: Database connection string

### Algorithm Parameters
- Interaction weights: `{'view': 1, 'like': 2, 'cart': 3, 'purchase': 5}`
- Hybrid weights: `{'collaborative': 0.6, 'content': 0.4}`
- TF-IDF parameters: `max_features=1000, stop_words='english'`

## Performance Considerations

- **Database Indexing**: Consider adding indexes on frequently queried columns
- **Caching**: Implement Redis caching for recommendation results
- **Batch Processing**: Process recommendations in batches for better performance
- **Model Persistence**: Save trained models to avoid retraining

## 🧪 Testing

### Manual Testing
1. Start the backend server
2. Open the frontend dashboard
3. Select different users and algorithms
4. Verify recommendations and explanations

### API Testing
```bash
# Get recommendations for user 1
curl "http://localhost:5000/api/users/1/recommendations?algorithm=hybrid&n=5"

# Add user interaction
curl -X POST "http://localhost:5000/api/users/1/interactions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 2, "interaction_type": "like", "rating": 5}'
```

## Deployment

### Production Setup
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (Gunicorn)
3. Set up a production database (PostgreSQL)
4. Configure environment variables securely
5. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## API Documentation

### Response Format
```json
{
  "product": {
    "id": 1,
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality wireless headphones...",
    "category": "Electronics",
    "price": 199.99,
    "brand": "TechSound",
    "rating": 4.5,
    "image_url": "https://...",
    "features": {
      "battery_life": "30 hours",
      "noise_cancellation": "Active"
    }
  },
  "score": 0.85,
  "explanation": "Based on your recent purchases of fitness-related electronics..."
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- Flask and React communities for excellent documentation
- Unsplash for providing product images

## Demo Video




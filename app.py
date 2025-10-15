import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import openai
from dotenv import load_dotenv
import json
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecommerce_recommender.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'sslmode': 'require'}
}

# Initialize Supabase connection
supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("Warning: Supabase URL or key not found. Check your .env file.")

db = SQLAlchemy(app)

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    brand = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    features = db.Column(db.Text)  # JSON string of features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserBehavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # Anonymous session ID
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    behavior_type = db.Column(db.String(50), nullable=False)  # view, purchase, add_to_cart
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    recommended_product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    recommendation_score = db.Column(db.Float)
    explanation = db.Column(db.Text)  # LLM-generated "Why this product?"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Recommendation Engine
class RecommendationEngine:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def get_product_recommendations(self, product_id, session_id=None, n_recommendations=5):
        """Get product recommendations based on a product"""
        # First check if we have pre-computed recommendations
        existing_recs = Recommendation.query.filter_by(source_product_id=product_id).all()
        
        if existing_recs:
            # Return existing recommendations
            recommendations = []
            for rec in existing_recs:
                product = Product.query.get(rec.recommended_product_id)
                if product:
                    recommendations.append({
                        'product_id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'price': product.price,
                        'image_url': product.image_url,
                        'score': rec.recommendation_score,
                        'explanation': rec.explanation
                    })
            return recommendations[:n_recommendations]
        
        # If no existing recommendations, generate new ones
        return self.generate_content_based_recommendations(product_id, n_recommendations)
    
    def generate_content_based_recommendations(self, product_id, n_recommendations=5):
        """Generate content-based recommendations"""
        # Get all products
        products = Product.query.all()
        
        if not products:
            return []
        
        # Create product feature matrix
        product_data = []
        for product in products:
            features = product.features if product.features else '{}'
            product_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'brand': product.brand,
                'features': features
            })
        
        df = pd.DataFrame(product_data)
        
        # Combine text features for similarity calculation
        df['combined_features'] = df['name'] + ' ' + df['description'] + ' ' + df['category'] + ' ' + df['brand']
        
        # Calculate similarity
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(df['combined_features'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Get recommendations
        source_product_index = df[df['id'] == product_id].index[0]
        similar_products = list(enumerate(cosine_sim[source_product_index]))
        similar_products = sorted(similar_products, key=lambda x: x[1], reverse=True)
        similar_products = similar_products[1:n_recommendations+1]  # Skip the first one (itself)
        
        # Get recommended product details
        recommendations = []
        for i, score in similar_products:
            product_id = df.iloc[i]['id']
            product = Product.query.get(product_id)
            
            # Generate explanation using LLM
            explanation = self.generate_explanation(product, df.iloc[source_product_index])
            
            # Save recommendation to database
            self.save_recommendation(df.iloc[source_product_index]['id'], product_id, score, explanation)
            
            recommendations.append({
                'product_id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'image_url': product.image_url,
                'score': float(score),
                'explanation': explanation
            })
        
        return recommendations
    
    def generate_explanation(self, recommended_product, source_product):
        """Generate explanation for recommendation using OpenAI"""
        try:
            prompt = f"""
            Source Product: {source_product['name']}
            Source Description: {source_product['description']}
            Source Category: {source_product['category']}
            
            Recommended Product: {recommended_product.name}
            Recommended Description: {recommended_product.description}
            Recommended Category: {recommended_product.category}
            
            Generate a brief, persuasive explanation (max 50 words) for why someone interested in the source product 
            would also like the recommended product. Start with "Because you viewed" and focus on key similarities or complementary features.
            """
            
            if not openai.api_key:
                print("OpenAI API key not found. Using default explanation.")
                return f"Because you viewed {source_product['name']}, you might also like this {recommended_product.category} product."
                
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful product recommendation assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                
                explanation = response.choices[0].message.content.strip()
                return explanation
            except Exception as e:
                print(f"Error with OpenAI API: {e}")
                # Fall back to client.chat.completions.create if the old method fails
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=openai.api_key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful product recommendation assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100,
                        temperature=0.7
                    )
                    explanation = response.choices[0].message.content.strip()
                    return explanation
                except Exception as e2:
                    print(f"Error with OpenAI client API: {e2}")
                    return f"Because you viewed {source_product['name']}, you might also like this {recommended_product.category} product."
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return f"Because you viewed {source_product['name']}, you might also like this {recommended_product.category} product."
    
    def save_recommendation(self, source_product_id, recommended_product_id, score, explanation):
        """Save recommendation to database"""
        # Check if recommendation already exists
        existing = Recommendation.query.filter_by(
            source_product_id=source_product_id,
            recommended_product_id=recommended_product_id
        ).first()
        
        if existing:
            # Update existing recommendation
            existing.recommendation_score = float(score)
            existing.explanation = explanation
            existing.created_at = datetime.utcnow()
        else:
            # Create new recommendation
            new_rec = Recommendation(
                source_product_id=source_product_id,
                recommended_product_id=recommended_product_id,
                recommendation_score=float(score),
                explanation=explanation
            )
            db.session.add(new_rec)
        db.session.commit()
            
    def search_products(self, query, n_recommendations=5):
        """Search products based on user query and provide recommendations"""
        if not query:
            return []
            
        # Search for products matching the query
        search_term = f"%{query}%"
        try:
            products = Product.query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.category.ilike(search_term)
                )
            ).all()
            
            if not products:
                return []
                
            # Get product details
            results = []
            for product in products:
                # Get recommendations for this product
                recommendations = self.get_product_recommendations(product.id, n_recommendations=3)
                
                results.append({
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'price': product.price,
                        'image_url': product.image_url,
                        'category': product.category
                    },
                    'recommendations': recommendations
                })
                
            return results
        except Exception as e:
            print(f"Error searching products: {e}")
            return []

        # Get all products
        all_products = Product.query.all()
        product_ids = [p.id for p in all_products]
        
        # Find similar users (simplified approach)
        similar_users = self._find_similar_users(user_id, df)
        
        # Calculate recommendation scores
        recommendations = []
        for product_id in product_ids:
            if product_id not in df['product_id'].values:
                score = self._calculate_collaborative_score(product_id, similar_users, df)
                if score > 0:
                    recommendations.append((product_id, score))
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def content_based_filtering(self, user_id, n_recommendations=5):
        """Content-based filtering using product features"""
        # Get user's liked products
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).all()
        liked_products = [i.product_id for i in user_interactions if i.interaction_type in ['like', 'purchase']]
        
        if not liked_products:
            return []
        
        # Get product features
        products = Product.query.all()
        product_features = {}
        
        for product in products:
            features = []
            if product.description:
                features.append(product.description)
            if product.category:
                features.append(product.category)
            if product.brand:
                features.append(product.brand)
            if product.features:
                try:
                    feature_dict = json.loads(product.features)
                    features.extend(feature_dict.values())
                except:
                    pass
            
            product_features[product.id] = ' '.join(features)
        
        # Create TF-IDF matrix
        product_texts = list(product_features.values())
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_texts)
        
        # Calculate user profile
        user_profile = np.zeros(tfidf_matrix.shape[1])
        for product_id in liked_products:
            if product_id in product_features:
                product_idx = list(product_features.keys()).index(product_id)
                user_profile += tfidf_matrix[product_idx].toarray()[0]
        
        user_profile = user_profile / len(liked_products)
        
        # Calculate similarities
        recommendations = []
        for i, (product_id, _) in enumerate(product_features.items()):
            if product_id not in liked_products:
                similarity = cosine_similarity([user_profile], [tfidf_matrix[i].toarray()[0]])[0][0]
                recommendations.append((product_id, similarity))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def _find_similar_users(self, user_id, df):
        """Find users with similar interaction patterns"""
        user_interactions = df[df['user_id'] == user_id]['product_id'].tolist()
        other_users = df[df['user_id'] != user_id]['user_id'].unique()
        
        similar_users = []
        for other_user in other_users:
            other_interactions = df[df['user_id'] == other_user]['product_id'].tolist()
            common_products = set(user_interactions) & set(other_interactions)
            
            if len(common_products) > 0:
                similarity = len(common_products) / len(set(user_interactions) | set(other_interactions))
                similar_users.append((other_user, similarity))
        
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:5]  # Top 5 similar users
    
    def _calculate_collaborative_score(self, product_id, similar_users, df):
        """Calculate recommendation score using collaborative filtering"""
        score = 0
        total_weight = 0
        
        for user_id, similarity in similar_users:
            user_rating = df[(df['user_id'] == user_id) & (df['product_id'] == product_id)]
            if not user_rating.empty:
                weighted_rating = user_rating['weighted_rating'].iloc[0]
                score += weighted_rating * similarity
                total_weight += similarity
        
        return score / total_weight if total_weight > 0 else 0

# Initialize recommendation engine
rec_engine = RecommendationEngine()

# API Routes
@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'E-commerce Recommendation API is running',
        'endpoints': {
            'products': '/api/products',
            'recommendations': '/api/recommendations/product/<product_id>',
            'search': '/api/search?query=<search_term>'
        }
    })

@app.route('/frontend.html')
def serve_frontend():
    return send_from_directory('.', 'frontend.html')

@app.route('/api/search', methods=['GET'])
def search_products_api():
    """Search products based on user query and provide recommendations"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query parameter is required'
            }), 400
            
        # Get session ID from request or generate a new one
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))
        
        # Search products
        results = rec_engine.search_products(query)
        
        response = jsonify({
            'status': 'success',
            'query': query,
            'results': results
        })
        
        # Set session cookie
        response.set_cookie('session_id', session_id, max_age=60*60*24*30)  # 30 days
        
        return response
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    query = request.args.get('query', '')
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Search query is required'
        }), 400
    
    # Get session ID from request or generate a new one
    session_id = request.cookies.get('session_id', str(uuid.uuid4()))
    
    # Search products
    results = rec_engine.search_products(query)
    
    return jsonify({
        'status': 'success',
        'query': query,
        'results': results
    })

@app.route('/api/recommendations/product/<int:product_id>')
def get_product_recommendations(product_id):
    """Get recommendations based on a product"""
    try:
        # Get session ID from request or generate a new one
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))
        
        # Record view behavior
        record_product_view(product_id, session_id)
        
        # Get recommendations
        recommendations = rec_engine.get_product_recommendations(product_id)
        
        return jsonify({
            'status': 'success',
            'product_id': product_id,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def record_product_view(product_id, session_id):
    """Record product view behavior"""
    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return
        
        # Record behavior
        behavior = UserBehavior(
            session_id=session_id,
            product_id=product_id,
            behavior_type='view'
        )
        db.session.add(behavior)
        db.session.commit()
    except Exception as e:
        print(f"Error recording product view: {e}")
        db.session.rollback()

# API Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products from database"""
    try:
        products = Product.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'price': p.price,
            'brand': p.brand,
            'image_url': p.image_url,
            'features': json.loads(p.features) if p.features else {}
        } for p in products])
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch products from database'
        }), 500

@app.route('/api/session', methods=['GET'])
def get_session():
    """Get or create anonymous session"""
    user = get_or_create_session()
    return jsonify({
        'session_id': user.session_id,
        'user_id': user.id,
        'preferences': json.loads(user.preferences) if user.preferences else {}
    })

@app.route('/api/interactions', methods=['POST'])
def add_interaction():
    """Add user interaction"""
    user = get_or_create_session()
    data = request.json
    
    interaction = UserInteraction(
        user_id=user.id,
        product_id=data['product_id'],
        interaction_type=data['interaction_type'],
        rating=data.get('rating')
    )
    db.session.add(interaction)
    db.session.commit()
    return jsonify({'message': 'Interaction added successfully'})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get product recommendations for current session"""
    user = get_or_create_session()
    algorithm = request.args.get('algorithm', 'hybrid')
    n_recommendations = int(request.args.get('n', 5))
    
    recommendations = []
    
    if algorithm == 'collaborative':
        recs = rec_engine.collaborative_filtering(user.id, n_recommendations)
    elif algorithm == 'content':
        recs = rec_engine.content_based_filtering(user.id, n_recommendations)
    else:  # hybrid
        collab_recs = rec_engine.collaborative_filtering(user.id, n_recommendations)
        content_recs = rec_engine.content_based_filtering(user.id, n_recommendations)
        
        # Combine recommendations
        rec_dict = {}
        for product_id, score in collab_recs:
            rec_dict[product_id] = score * 0.6  # Collaborative weight
        for product_id, score in content_recs:
            if product_id in rec_dict:
                rec_dict[product_id] += score * 0.4  # Content weight
            else:
                rec_dict[product_id] = score * 0.4
        
        recs = sorted(rec_dict.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    
    # Get product details and generate explanations
    for product_id, score in recs:
        product = Product.query.get(product_id)
        if product:
            # Generate LLM explanation
            explanation = generate_explanation(user.id, product_id, score, algorithm)
            
            # Save recommendation
            recommendation = Recommendation(
                user_id=user.id,
                product_id=product_id,
                score=score,
                explanation=explanation,
                algorithm=algorithm
            )
            db.session.add(recommendation)
            
            recommendations.append({
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category': product.category,
                    'price': product.price,
                    'brand': product.brand,
                    'rating': product.rating,
                    'image_url': product.image_url,
                    'features': json.loads(product.features) if product.features else {}
                },
                'score': score,
                'explanation': explanation
            })
    
    db.session.commit()
    return jsonify(recommendations)

def generate_explanation(user_id, product_id, score, algorithm):
    """Generate LLM-powered explanation for recommendation"""
    try:
        # Get user and product information
        user = User.query.get(user_id)
        product = Product.query.get(product_id)
        
        # Get user's recent interactions
        recent_interactions = UserInteraction.query.filter_by(user_id=user_id)\
            .order_by(UserInteraction.timestamp.desc()).limit(5).all()
        
        interaction_summary = []
        for interaction in recent_interactions:
            interacted_product = Product.query.get(interaction.product_id)
            interaction_summary.append(f"- {interaction.interaction_type} {interacted_product.name}")
        
        # Create prompt for LLM
        prompt = f"""
        Explain why the product "{product.name}" (${product.price}) is recommended to user "{user.name}" based on their behavior.
        
        User's recent activity:
        {chr(10).join(interaction_summary) if interaction_summary else "No recent activity"}
        
        Product details:
        - Category: {product.category}
        - Brand: {product.brand}
        - Description: {product.description}
        - Rating: {product.rating}/5
        
        Recommendation algorithm: {algorithm}
        Recommendation score: {score:.2f}
        
        Provide a brief, personalized explanation (2-3 sentences) explaining why this product would be a good fit for this user.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful e-commerce assistant that explains product recommendations in a friendly, personalized way."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"This product matches your preferences and has a high recommendation score of {score:.2f}."

@app.route('/api/interactions', methods=['GET'])
def get_user_interactions():
    """Get current session's interaction history"""
    user = get_or_create_session()
    interactions = UserInteraction.query.filter_by(user_id=user.id)\
        .order_by(UserInteraction.timestamp.desc()).all()
    
    return jsonify([{
        'id': i.id,
        'product_id': i.product_id,
        'interaction_type': i.interaction_type,
        'rating': i.rating,
        'timestamp': i.timestamp.isoformat()
    } for i in interactions])

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

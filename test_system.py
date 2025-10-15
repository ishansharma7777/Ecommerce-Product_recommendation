#!/usr/bin/env python3
"""
Test script for E-commerce Product Recommender
Tests the API endpoints and recommendation functionality
"""

import requests
import json
import time
import sys

API_BASE_URL = 'http://localhost:5001/api'

def test_api_connection():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/products", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_get_products():
    """Test getting products"""
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Retrieved {len(products)} products")
            return products
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return None

def test_get_recommendations(algorithm='hybrid'):
    """Test getting recommendations"""
    try:
        url = f"{API_BASE_URL}/recommendations"
        params = {'algorithm': algorithm, 'n': 3}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Retrieved {len(recommendations)} recommendations")
            
            # Print first recommendation details
            if recommendations:
                rec = recommendations[0]
                print(f"   📦 Product: {rec['product']['name']}")
                print(f"   💰 Price: ${rec['product']['price']}")
                print(f"   📊 Score: {rec['score']:.3f}")
                print(f"   💡 Explanation: {rec['explanation'][:100]}...")
            
            return recommendations
        else:
            print(f"❌ Failed to get recommendations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        return None

def test_user_interactions():
    """Test getting user interactions"""
    try:
        response = requests.get(f"{API_BASE_URL}/interactions")
        if response.status_code == 200:
            interactions = response.json()
            print(f"✅ Retrieved {len(interactions)} interactions")
            return interactions
        else:
            print(f"❌ Failed to get interactions: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting interactions: {e}")
        return None

def test_different_algorithms():
    """Test different recommendation algorithms"""
    algorithms = ['collaborative', 'content', 'hybrid']
    
    print("\n🧪 Testing different algorithms:")
    for algo in algorithms:
        print(f"\n📊 Testing {algo} algorithm:")
        recommendations = test_get_recommendations(algo)
        if recommendations:
            print(f"   ✅ {algo} algorithm working")
        else:
            print(f"   ❌ {algo} algorithm failed")

def main():
    """Run all tests"""
    print("🧪 E-commerce Product Recommender Test Suite")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ Cannot connect to API. Make sure the Flask server is running.")
        print("   Run: python app.py")
        sys.exit(1)
    
    # Test getting products
    print("\n📦 Testing product retrieval:")
    products = test_get_products()
    if not products:
        sys.exit(1)
    
    # Test getting user interactions
    print("\n👤 Testing user interactions:")
    interactions = test_user_interactions()
    
    # Test getting recommendations
    print("\n🎯 Testing recommendations:")
    recommendations = test_get_recommendations()
    if not recommendations:
        sys.exit(1)
    
    # Test different algorithms
    test_different_algorithms()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("\n🌐 Frontend available at: http://localhost:8000/frontend.html")
    print("🔗 API available at: http://localhost:5001")

if __name__ == "__main__":
    main()

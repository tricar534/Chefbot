from flask import Flask, request, jsonify
from flask_cors import CORS
from intents import determine_intent
from recommender import (
    search_recipes_by_ingredients,
    filter_by_diet,
    format_recipe_response,
    get_recipe_by_id,
    format_recipe_details,
    get_recipe_count
)
import logging

app = Flask(__name__)

# Enable CORS for all origins (use specific origins in production)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # For development - restrict in production
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log recipe count at startup
recipe_count = get_recipe_count()
logger.info(f"Database contains {recipe_count} recipes")


@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            logger.warning("No JSON data received")
            return jsonify({
                "response": "No message received. Please send a valid message.",
                "error": True
            }), 400
        
        user_message = data.get('message', '')
        logger.info(f"Received message: '{user_message}'")
        
        if not user_message:
            logger.warning("Empty message received")
            return jsonify({
                "response": "Please enter a message.",
                "error": True
            }), 400
        
        # Process the message through intent detection
        intent_data = determine_intent(user_message)
        logger.info(f"Detected intent: {intent_data['intent']}")
        
        response_text = ""
        
        # Handle different intents
        if intent_data['intent'] == 'greeting':
            response_text = "Hello! I'm Chefbot 👨‍🍳 Tell me what ingredients you have and I'll suggest some recipes!"
        
        elif intent_data['intent'] == 'ingredient_search':
            ingredients = intent_data['ingredients']
            diet_restrictions = intent_data['diet_restrictions']
            
            if not ingredients:
                response_text = "Please tell me what ingredients you have. For example: 'I have chicken, rice, and tomatoes'"
            else:
                logger.info(f"Searching recipes for ingredients: {ingredients}, diet: {diet_restrictions}")
                
                # Search for recipes (no ALL_RECIPES needed - it queries the DB directly)
                results = search_recipes_by_ingredients(ingredients, max_results=5)
                
                # Filter by diet if specified
                if diet_restrictions:
                    results = filter_by_diet(results, diet_restrictions)
                
                response_text = format_recipe_response(results, ingredients)
        
        elif intent_data['intent'] == 'meal_plan':
            response_text = "Meal planning feature coming soon! For now, tell me what ingredients you have and I'll find recipes for you."
        
        elif intent_data['intent'] == 'diet_restrictions':
            diet = intent_data['diet_restrictions']
            response_text = f"Got it! Looking for {', '.join(diet)} recipes. What ingredients do you have?"
        
        else:
            response_text = "I can help you find recipes! Tell me what ingredients you have, like 'I have chicken and rice'"

        return jsonify({
            "response": response_text, 
            "intent_data": intent_data,
            "error": False
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return jsonify({
            "response": "Sorry, something went wrong processing your message!",
            "error": True,
            "error_details": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "chefbot-backend"
    }), 200


@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "message": "Chefbot Backend API",
        "endpoints": {
            "/chat": "POST - Send a message to the chatbot",
            "/health": "GET - Health check"
        }
    }), 200


if __name__ == '__main__':
    logger.info("Starting Chefbot Backend Server...")
    logger.info("Server running on http://0.0.0.0:5000")
    logger.info("Press CTRL+C to quit")
    
    # Run with debug mode for development
    app.run(host='0.0.0.0', port=5000, debug=True)
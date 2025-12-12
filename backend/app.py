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

# Store last search results per session (simple in-memory storage)
# In production, you'd use Redis or a proper session store
last_search_results = {}
user_sessions = {}  # Store user preferences (diet, etc.)


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
        
        # Generate a simple session ID (in production, use proper session management)
        # For now, we'll use a simple approach - store globally (works for single user testing)
        session_id = "default"
        
        # Initialize session if it doesn't exist
        if session_id not in user_sessions:
            user_sessions[session_id] = {
                'diet_restrictions': [],
                'last_intent': None
            }
        
        response_text = ""
        
        # Handle different intents
        if intent_data['intent'] == 'greeting':
            # Show current diet restrictions if any
            current_diet = user_sessions[session_id]['diet_restrictions']
            diet_info = f"\n🔖 Active diet filter: {', '.join(current_diet)}" if current_diet else ""
            
            response_text = (
                "Hello! I'm Chefbot 👨‍🍳\n\n"
                "Tell me what you'd like to cook:\n"
                "• 'I have [ingredients]' - Find recipes with your ingredients\n"
                "• 'I want a [diet] meal' - Set diet for next search (one-time use)\n"
                "• 'I want a [diet] with [ingredients]' - Search with diet filter\n"
                "• 'remove [diet]' or 'clear diet' - Remove diet restrictions\n\n"
                f"Example: 'I want a vegan meal' then 'I have rice and beans'{diet_info}\n\n"
                f"💡 Diet filters auto-clear after each search!"
            )
        
        elif intent_data['intent'] == 'ingredient_search':
            ingredients = intent_data['ingredients']
            diet_restrictions = intent_data['diet_restrictions']
            
            # If no diet restrictions in current message, use stored ones
            if not diet_restrictions and user_sessions[session_id]['diet_restrictions']:
                diet_restrictions = user_sessions[session_id]['diet_restrictions']
                logger.info(f"Using stored diet restrictions: {diet_restrictions}")
            
            # Store diet restrictions if provided
            if diet_restrictions:
                user_sessions[session_id]['diet_restrictions'] = diet_restrictions
            
            if not ingredients:
                response_text = "Please tell me what ingredients you have. For example: 'I have chicken, rice, and tomatoes'"
            else:
                logger.info(f"Searching recipes for ingredients: {ingredients}, diet: {diet_restrictions}")
                
                # Search for more recipes if diet filter is applied (many will be filtered out)
                search_limit = 20 if diet_restrictions else 10
                
                # Search for recipes (no ALL_RECIPES needed - it queries the DB directly)
                results = search_recipes_by_ingredients(ingredients, max_results=search_limit)
                logger.info(f"Found {len(results)} recipes before filtering")
                
                # Filter by diet if specified
                if diet_restrictions:
                    logger.info(f"Applying diet filter: {diet_restrictions}")
                    results = filter_by_diet(results, diet_restrictions)
                    logger.info(f"Recipes after diet filter: {len(results)}")
                
                # Store results for later detail requests
                last_search_results[session_id] = results
                
                response_text = format_recipe_response(results, ingredients)
                
                # Clear diet restrictions after showing recipes (one-time use)
                if user_sessions[session_id]['diet_restrictions']:
                    user_sessions[session_id]['diet_restrictions'] = []
                    logger.info("Auto-cleared diet restrictions after showing results")
                
                # Add note if using stored diet preferences
                if diet_restrictions and not intent_data['diet_restrictions']:
                    response_text += f"\n\n🔖 Filtered by: {', '.join(diet_restrictions)} (from your previous request)"
                
                # Clear diet restrictions after showing recipes (one-time use)
                if user_sessions[session_id]['diet_restrictions']:
                    user_sessions[session_id]['diet_restrictions'] = []
                    logger.info("Auto-cleared diet restrictions after showing results")
        
        elif intent_data['intent'] == 'meal_plan':
            response_text = "Meal planning feature coming soon! For now, tell me what ingredients you have and I'll find recipes for you."
        
        elif intent_data['intent'] == 'diet_restrictions':
            diet = intent_data['diet_restrictions']
            ingredients = intent_data['ingredients']
            
            # Store diet restrictions in session
            if diet:
                user_sessions[session_id]['diet_restrictions'] = diet
                logger.info(f"Stored diet restrictions in session: {diet}")
            
            # If they provided ingredients with diet, search now
            if ingredients:
                logger.info(f"Searching recipes for ingredients: {ingredients}, diet: {diet}")
                
                # Search for more recipes when diet filter is applied
                search_limit = 20 if diet else 10
                results = search_recipes_by_ingredients(ingredients, max_results=search_limit)
                logger.info(f"Found {len(results)} recipes before filtering")
                
                if diet:
                    logger.info(f"Applying diet filter: {diet}")
                    results = filter_by_diet(results, diet)
                    logger.info(f"Recipes after diet filter: {len(results)}")
                
                # Store results for later detail requests
                last_search_results[session_id] = results
                
                response_text = format_recipe_response(results, ingredients)
            else:
                # No ingredients provided, ask for them
                response_text = f"Got it! I'll look for {', '.join(diet)} recipes. What ingredients do you have?"
        
        elif intent_data['intent'] == 'recipe_detail':
            recipe_number = intent_data.get('recipe_number')
            
            # Check if we have stored results
            if session_id not in last_search_results or not last_search_results[session_id]:
                response_text = "Please search for recipes first! Try: 'I have chicken and rice'"
            elif recipe_number < 1 or recipe_number > len(last_search_results[session_id]):
                response_text = f"Please enter a number between 1 and {len(last_search_results[session_id])}"
            else:
                # Get the recipe (subtract 1 for 0-indexed array)
                recipe = last_search_results[session_id][recipe_number - 1]
                response_text = format_recipe_details(recipe)
        
        elif intent_data['intent'] == 'clear_diet':
            # Clear stored diet restrictions
            cleared_diets = user_sessions[session_id]['diet_restrictions'].copy()
            user_sessions[session_id]['diet_restrictions'] = []
            logger.info("Cleared diet restrictions from session")
            
            if cleared_diets:
                response_text = f"✅ Removed {', '.join(cleared_diets)} filter. You can now search for any recipes!"
            else:
                response_text = "✅ No diet restrictions were active. You can search for any recipes!"
        
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
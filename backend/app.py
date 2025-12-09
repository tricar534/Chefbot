from flask import Flask, request, jsonify
from flask_cors import CORS
from intents import determine_intent
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
        
        # Format response for UI
        response_text = (
            f"Intent: {intent_data['intent']} | "
            f"Ingredients: {intent_data['ingredients']} | "
            f"Diet: {intent_data['diet_restrictions']}"
        )

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
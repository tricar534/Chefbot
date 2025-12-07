from flask import Flask, request, jsonify
from flask_cors import CORS

from intents import determine_intent

app = Flask(__name__)
# Enable CORS to allow the React frontend to communicate with the Flask backend
CORS(app)


@app.route('/chat', methods=['POST'])
def chat():
    # If request is none => {}
    data = request.get_json() or {} 
    user_message = data.get('message', '')

    intent_data = determine_intent(user_message)

    # Temp readable message for UI
    response_text =(
        f"Intent: {intent_data['intent']} | "
        f"Ingredients: {intent_data['ingredients']} | "
        f"Diet: {intent_data['diet_restrictions']}"
    )

    return jsonify({
        "response": response_text, 
        "intent_data": intent_data    
    })

if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    app.run(host='0.0.0.0', port=5000)

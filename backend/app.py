from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS to allow the React frontend to communicate with the Flask backend
CORS(app)

# Simple rule-based response logic
def get_bot_response(user_input):
    user_input = user_input.lower()
    if "hello" in user_input or "hi" in user_input:
        return "Hi there! I'm a simple local bot."
    elif "how are you" in user_input:
        return "I'm doing great, thanks for asking!"
    elif "bye" in user_input or "quit" in user_input:
        return "Goodbye! Have a nice day."
    else:
        return "Sorry, I didn't understand that. Try asking about 'hello' or 'bye'."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    bot_response = get_bot_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    app.run(host='0.0.0.0', port=5000)

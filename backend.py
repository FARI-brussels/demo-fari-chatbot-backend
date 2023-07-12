import openai
import json
from flask import Flask, request, jsonify
import uuid

with open("./keys.json", 'r') as j:
    keys = json.loads(j.read())
    openai.api_key = keys["OPENAI_API_KEY"]
# Import required modules

CONVERSATIONS = {}

# Initialize the Flask application
app = Flask(__name__)

@app.route('/initiate', methods=['GET'])
def initiate():
    # Generate a unique UUID for the new conversation
    conversation_id = str(uuid.uuid4())
    CONVERSATIONS[conversation_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    # Return the conversation ID to the client
    return jsonify({'conversation_id': conversation_id})



# Define a route for the default URL, which loads the chatbot
@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Get user message from POST request
    try:
        user_message = request.json['message']
        conversation_id = request.json['conversation_id']
    except KeyError:
        return jsonify({'error': 'No message provided'}), 400
    if conversation_id not in CONVERSATIONS:
        return jsonify({'error': 'Invalid conversation_id'}), 400
    # Here you would typically process the message and get a response from your chatbot
    # For simplicity, we just echo the message back to the user
    CONVERSATIONS[conversation_id] += [{"role": "user", "content": f"{user_message}"}]
    # given the most recent context (4096 characters)
    # continue the text up to 2048 tokens ~ 8192 charaters
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=CONVERSATIONS[conversation_id],
        max_tokens = 2048,
        temperature = 0.4, # Lower values make responses more deterministic
    )
    # append response to context
    response = completion.choices[0].message
    CONVERSATIONS[conversation_id] += [response]
    
    return jsonify({'message':response.content, "context":CONVERSATIONS[conversation_id]})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


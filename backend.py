import openai
import json
from flask import Flask, request, jsonify
import uuid
import os
import tiktoken
import requests
from pypdf import PdfReader


with open("./keys.json", 'r') as j:
    keys = json.loads(j.read())
    openai.api_key = keys["OPENAI_API_KEY"]
# Import required modules
ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
MAX_TOKENS = 8000
url = 'https://arxiv.org/pdf/2307.03027.pdf'
CONVERSATIONS = {}


def download_and_extract(pdf_url):
    # Step 1: Download the PDF
    response = requests.get(pdf_url)
    with open('my_paper.pdf', 'wb') as f:
        f.write(response.content)

    # Step 2: Extract the text
    with open('my_paper.pdf', 'rb') as f:
        reader = PdfReader(f)
        number_of_pages = len(reader.pages)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    text = trim_text(text, ENCODING)

    return text

 
def trim_text(text: str, encoding) -> int:
    """Returns the number of tokens in a text string."""
    trimed_text=text[:22000]
    num_tokens = len(encoding.encode(trimed_text))
    i = 0
    while num_tokens<MAX_TOKENS:
        num_tokens = len(encoding.encode(trimed_text))
        trimed_text=text[:22000 + i*100]
        i+=1
    return text[:22000 + (i-2)*100] 



# Initialize the Flask application
app = Flask(__name__)
@app.route('/initiate', methods=['GET'])
def initiate():
    # Generate a unique UUID for the new conversation
    conversation_id = str(uuid.uuid4())

    # Get the PDF URL from the URL parameters
    pdf_url = request.args.get('pdf_url')
    print(pdf_url)

    if pdf_url:
        pdf_text= download_and_extract(pdf_url)
        CONVERSATIONS[conversation_id] = [{"role": "system", "content": f"You are an helpful scientific assistant answering question about this article : \n {pdf_text}"}]
        
    else:
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
        model='gpt-3.5-turbo-16k',
        messages=CONVERSATIONS[conversation_id],
        max_tokens = 8094,
        temperature = 0.4, # Lower values make responses more deterministic
    )
    # append response to context
    response = completion.choices[0].message
    
    CONVERSATIONS[conversation_id] += [response]
    return jsonify({'message':response.content, "context":CONVERSATIONS[conversation_id]})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




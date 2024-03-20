from openai import OpenAI
import json
from flask import Flask, request, jsonify
import uuid
import tiktoken
import requests
from pypdf import PdfReader
from flask_cors import CORS
import datetime

with open("./keys.json", 'r') as j:
    keys = json.loads(j.read())

# Import required modules
ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
MAX_TOKENS = 8000
CONVERSATIONS = {}
TIMESTAMPS = {}

client = OpenAI(
        # This is the default and can be omitted
        api_key=keys["OPENAI_API_KEY"],
    )


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
    if len(ENCODING.encode(text))>MAX_TOKENS:
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
CORS(app)
@app.route('/initiate', methods=['GET'])
def initiate():
    # Generate a unique UUID for the new conversation
    conversation_id = str(uuid.uuid4())

    # Get the PDF URL from the URL parameters
    pdf_url = request.args.get('pdf_url')

    if pdf_url:
        try:
            pdf_text= download_and_extract(pdf_url)
            CONVERSATIONS[conversation_id] = [{"role": "system", "content": f"You are an helpful assistant answering question about this pdf : \n {pdf_text}"}]
        except requests.exceptions.MissingSchema:
            return "Invalid pdf url", 400

    else:
        CONVERSATIONS[conversation_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    TIMESTAMPS[conversation_id] = datetime.datetime.now()
    
    # Delete conversations older than 10 minutes
    current_time = datetime.datetime.now()
    conv_to_delete = [cid for cid, timestamp in TIMESTAMPS.items() if (current_time - timestamp).total_seconds() > 600]  # 600 seconds = 10 minutes

    for cid in conv_to_delete:
        del CONVERSATIONS[cid]
        del TIMESTAMPS[cid]

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
    try:
        response = get_gpt_response(CONVERSATIONS[conversation_id]) 
    except Exception as e:
        print(e)
        CONVERSATIONS[conversation_id] = [CONVERSATIONS[conversation_id][0]] + [{"role": "user", "content": f"{user_message}"}]
        response = get_gpt_response(CONVERSATIONS[conversation_id])
    CONVERSATIONS[conversation_id] += [response]
    return jsonify({'message':response, "context":CONVERSATIONS[conversation_id]})

def get_gpt_response(message):

    

    completion = client.chat.completions.create(
        messages=message,
        model="gpt-4-turbo-preview",)
    response = completion.choices[0].message
    return response.content

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




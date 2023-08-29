# Flask Chatbot

A simple Flask application that can initiate a conversation and process messages for a chatbot. It includes two API endpoints: one to initiate a conversation, and another one to send and receive chatbot messages.

## Installation

First, clone the repository to your local machine:

```
git clone https://github.com/FARI-brussels/demo-fari-chatbot-backend.git
cd demo-fari-chatbot-backend
```

Then, install the dependencies : 
```
pip install -r requirements.txt
```
You can now run the server:
```
python -m backend
```
The server should be running at http://localhost:5000

## API endpoints

### GET /initiate
Initiates a new conversation and returns a unique conversation ID.

url : http://localhost:5000/initiate

query parameters : pdf_url (optional)

example : http://localhost:5000/initiate?pdf_url=http://example.com/mypdf.pdf

Response

200 OK on success
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}

```

### POST /chatbot
Initiates a new conversation and returns a unique conversation ID.

#### request
url : http://localhost:5000/chatbot

input data : 
```json data
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello, chatbot!"
}
```
Response

200 OK on success
```json
{
    "context": [],
    "message": "Hello user."
}

```
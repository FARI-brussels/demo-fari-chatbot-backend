import requests
from pypdf import PdfReader
import tiktoken
import math
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import json
import os

with open("./keys.json", 'r') as j:
    keys = json.loads(j.read())
    os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]


ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
LLM = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
MAX_TOKENS = 15000
url = 'https://arxiv.org/pdf/2307.03027.pdf'  # Replace with your URL

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


def ai_please_answer_my_questions(questions, text):
    #prompt= f"""I give you a scientific paper on AI and ask you several question on it \n {text}"""
    prompt = "My name is SImoen"
    _ = LLM.predict_messages([HumanMessage(content=prompt)]).content
    print(_)
    question1 = "What is my name"
    answer1 = LLM.predict_messages([HumanMessage(content=question1)]).content
    print(answer1)


def main():
    text = download_and_extract(url)
    ai_please_answer_my_questions("yo", text)

main()
import os
from flask import Flask, render_template, request, jsonify, flash
from werkzeug.utils import secure_filename
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the language model
groqllm = ChatGroq(model="llama3-8b-8192", temperature=0)
prompt = """(system: You are a cyber security assistant specialized only with cyber security and ethical hacking. If the user's question is related to cyber security, vulnerabilities, network security, ethical hacking concepts provide a detailed and helpful response. If the question is not related to cyber security and related, respond with "I'm sorry, I can only assist with Cyber Security queries.")
(user: Question: {question})"""
promptinstance = ChatPromptTemplate.from_template(prompt)

@app.route('/')
def index():
    return render_template('cybercare.html')

@app.route('/cybercare')
def cybercare():
    return render_template('cybercare.html')

@app.route('/speech')
def speech():
    return render_template('speech.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    logging.info(f"Received question: {question}")
    try:
        response = promptinstance | groqllm | StrOutputParser()
        answer = response.invoke({'question': question})

        formatted_answer = format_answer(answer)
        logging.info(f"Response generated: {formatted_answer}")
        return jsonify({'answer': formatted_answer})
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return jsonify({'answer': f'Error processing your request: {str(e)}'}), 500

def format_answer(answer):
    answer = answer.replace("**", "<strong>").replace("**", "</strong>")
    formatted_answer = "<div style='text-align: left;'>"
    lines = answer.split('\n')
    for line in lines:
        if line.strip():
            formatted_answer += f"<p>{line.strip()}</p>"
    formatted_answer += "</div>"
    return formatted_answer

if __name__ == '__main__':
    app.run(debug=True)

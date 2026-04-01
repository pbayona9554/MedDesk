from flask import Flask, request, jsonify, render_template
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route('/triage', methods=['POST'])
def triage():
    data = request.get_json()
    ticket = data["ticket"]

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"You are a ticket triage assistant. Here is the ticket: {ticket} you will read this ticket and determine its priority (low, medium, or high) then you will categorize it as a technical issue, billing issue, account issue, or a general issue. you will then provide a suggest a solution, and forward it to the corresponding department. respond using these exact labels: Priority: / Category: / Suggested Resolution: / Route To:"}
        ]
    )

    result = response.content[0].text
    return jsonify({"result": result})

@app.route('/qa', methods=['POST'])
def qa():

    data = request.get_json()
    question = data["question"]

    document = data["document"]

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"you are responding to a client in a health setting. using this document {document} you will answer their question {question}. please answer their question only using the information in the document, and if it's not available in the document tell the client you will escalate it to the correct department"}
        ]
    )
    
    result = response.content[0].text
    return jsonify({"result": result})

@app.route('/summarize', methods=['POST'])
def summarize():

    data = request.get_json()
    text = data["text"]

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"read the input {text} and respond with a headline(a sentence capturing the main point) the key points (the most imporant takeaways) the overall sentiment (the tone) and action items (anything that requires a follow-up and or decision)"}
        ]
    )

    result = response.content[0].text
    return jsonify({"result": result})

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True, port=5001)



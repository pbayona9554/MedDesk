from flask import Flask, request, jsonify, render_template, session
import anthropic
import os
from dotenv import load_dotenv
from data.policy import POLICY
from config.prompts import ACTIVE_PROMPT
from datetime import datetime, timedelta
from database import init_db, seed_db, get_patient

#load .env
load_dotenv()

#initialize and seed db 
init_db() 
seed_db()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=30)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def write_audit_log(name, policy_number, message, result, escalated):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] NAME: {name} | POLICY: {policy_number} | ESCALATED: {escalated}\nUSER: {message}\nMEDDESK: {result}\n---\n"
    with open("logs/audit.log", "a") as f:
        f.write(entry)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():

    data = request.get_json() #get message from request
    message = data["message"] 
    name = data.get("name", "Patient")
    name = " ".join(word.capitalize() for word in name.strip().split())
    policy_number = data.get("policy", "Unknown")

    patient = get_patient(policy_number)
    if patient:
        patient_context = f"Patient on file: Name: {patient[1]}, Plan: {patient[2]}, Deductible met: ${patient[3]}, Last Service: {patient[4]} on {patient[5]}"
    else:
        patient_context = "No patient record found for this policy number."
    
    conversation_history = session.get("history", []) #read from session
    conversation_history.append({"role": "user", "content": message}) #append new message

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=ACTIVE_PROMPT.format(policy=POLICY, patient_context=patient_context),
        messages=conversation_history #send to claude
    )
    
    result = response.content[0].text
    
    escalated = False

    if "ESCALATE: profanity" in result:
        result = result.replace("ESCALATE: profanity", "").strip()
        escalated = True
    
    if "ESCALATE: human requested" in result:
        result = result.replace("ESCALATE: human requested", "").strip()
        escalated = True

    write_audit_log(name, policy_number, message, result, escalated)
    conversation_history.append({"role": "assistant", "content": result}) #append response + save to session
    session["history"] = conversation_history

    return jsonify({"result": result, "escalated": escalated})

if __name__ == '__main__':
    app.run(debug = True, port=5001)
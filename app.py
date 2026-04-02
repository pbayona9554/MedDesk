from flask import Flask, request, jsonify, render_template, session
import anthropic
import os
from dotenv import load_dotenv
from data.policy import POLICY
from config.prompts import ACTIVE_PROMPT
from datetime import datetime, timedelta
from database import init_db, seed_db, get_patient
from ml.sentiment import analyze_sentiment

# Load environment variables from .env
load_dotenv()

# Initialize and seed the database on startup
init_db()
seed_db()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=30)

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def write_audit_log(name, policy_number, message, result, escalated, sentiment_label, sentiment_score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Includes sentiment data so we can analyze patient tone patterns over time
    entry = (
        f"[{timestamp}] NAME: {name} | POLICY: {policy_number} | "
        f"ESCALATED: {escalated} | SENTIMENT: {sentiment_label} ({sentiment_score})\n"
        f"USER: {message}\n"
        f"MEDDESK: {result}\n---\n"
    )
    with open("logs/audit.log", "a") as f:
        f.write(entry)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data["message"]
    name = data.get("name", "Patient")

    # Normalize patient name to title case
    name = " ".join(word.capitalize() for word in name.strip().split())
    policy_number = data.get("policy", "Unknown")

    # Look up patient record by policy number
    patient = get_patient(policy_number)
    if patient:
        patient_context = (
            f"Patient on file: Name: {patient[1]}, Plan: {patient[2]}, "
            f"Deductible met: ${patient[3]}, Last Service: {patient[4]} on {patient[5]}"
        )
    else:
        patient_context = "No patient record found for this policy number."

    # --- SENTIMENT ANALYSIS ---
    # Run the patient's message through our HuggingFace model before sending to Claude
    # Returns label (POSITIVE/NEGATIVE), confidence score, and a tone instruction for Claude
    sentiment = analyze_sentiment(message)
    sentiment_label = sentiment["label"]
    sentiment_score = sentiment["score"]
    tone_hint = sentiment["tone_hint"]

    # Read existing conversation history from session
    conversation_history = session.get("history", [])

    # Append the new patient message to history
    conversation_history.append({"role": "user", "content": message})

    # Send to Claude — tone_hint injected into system prompt so Claude
    # adjusts its response style based on the patient's detected emotion
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=ACTIVE_PROMPT.format(
            policy=POLICY,
            patient_context=patient_context,
            tone_hint=tone_hint
        ),
        messages=conversation_history
    )

    result = response.content[0].text

    # Check for escalation flags in Claude's response
    escalated = False
    if "ESCALATE: profanity" in result:
        result = result.replace("ESCALATE: profanity", "").strip()
        escalated = True
    if "ESCALATE: human requested" in result:
        result = result.replace("ESCALATE: human requested", "").strip()
        escalated = True

    # Write to audit log — now includes sentiment data
    write_audit_log(name, policy_number, message, result, escalated, sentiment_label, sentiment_score)

    # Append Claude's response to history and save back to session
    conversation_history.append({"role": "assistant", "content": result})
    session["history"] = conversation_history

    return jsonify({"result": result, "escalated": escalated})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

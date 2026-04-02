# MedDesk

An AI-powered patient help desk built with Flask, the Anthropic Claude API, and a real-time ML pipeline. MedDesk automates patient helpdesk workflows by analyzing patient messages, routing them by intent, and generating personalized responses grounded in each patient's plan data.

---

## What It Does

Patients enter their name and policy number, then chat with MedDesk in a conversational interface. Before each message reaches Claude, it passes through two ML models:

- **Sentiment analysis** — a DistilBERT model detects the patient's tone and instructs Claude to respond with the appropriate level of empathy
- **Intent classification** — a zero-shot BART model classifies the message into billing, coverage, escalation, or general, and routes it to a focused prompt

The assistant then:
- Looks up the patient by policy number in a SQLite database and injects their plan details into Claude's context
- Answers billing and coverage questions using a master policy document
- Maintains full conversation history within a session, allowing for follow-up questions
- Detects profanity and requests for human representatives and automatically escalates
- Logs every interaction to an audit trail

---

## Features

- **Patient database** — SQLite database stores patient records; policy number lookup at session start injects each patient directly into the AI's system prompt for personalized responses
- **Stateful conversation history** — full multi-turn context on every message so patients can ask follow-up questions
- **Smart escalation** — profanity triggers automatic escalation
- **Audit logging** — all interactions written to audit logs
- **Session expiry** — sessions expire after 30 minutes of inactivity

---

## Tech Stack

- **Python** — core language
- **Flask** — web framework and session management
- **Anthropic Claude API** — `claude-opus-4-5` via the `anthropic` Python SDK
- **HuggingFace Transformers** — DistilBERT and BART inference pipeline
- **SQLite** — lightweight patient database
- **Vanilla HTML/CSS/JS** — frontend

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/pbayona9554/MedDesk.git
cd MedDesk
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here
```

Get a personal Anthropic API key at [console.anthropic.com](https://console.anthropic.com).

**5. Run the app**
```bash
python3 app.py
```

Open `http://127.0.0.1:5001` in your browser.

---

## Future Improvements

- Raw PyTorch inference — rewrite sentiment model without pipeline wrapper
- Supabase — migrate patient database to cloud PostgreSQL
- Persistent session history — store conversation history across sessions
- Multi-model support — abstract AI layer to swap between Claude, GPT, Gemini
- RAG — replace hardcoded policy document with vector search over uploaded PDFs
- Escalation summary report — structured case summary generated on escalation

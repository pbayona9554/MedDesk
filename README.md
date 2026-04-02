# MedDesk

An AI-powered patient support chatbot built with Flask and the Anthropic Claude API. MedDesk automates patient helpdesk workflows by answering billing questions, explaining coverage, and escalating complex cases to human representatives — with personalized responses based on each patient's plan data.

---

## What It Does

Patients enter their name and policy number, then chat with MedDesk in a real-time conversational interface. The assistant:

- Looks up the patient by policy number in a SQLite database and injects their plan details into the AI's context for personalized responses
- Answers billing and coverage questions using a master policy document as its only knowledge source
- Maintains full conversation history within a session so patients can ask follow-up questions
- Detects profanity and automatically escalates the session to a human representative
- Logs every interaction to an audit trail with timestamps, escalation flags, and full message content

---

## Features

- **Patient database** — SQLite database stores patient records; policy number lookup at session start injects each patient's plan type, deductible status, and service history directly into the AI's system prompt for personalized responses
- **Patient intake** — name and policy number collected at session start, used throughout the conversation
- **Stateful conversation history** — full multi-turn context on every message so patients can ask follow-up questions
- **Master policy document** — loaded server-side; Claude answers only from this document
- **Smart escalation** — profanity triggers automatic escalation
- **Audit logging** — all interactions written to audit logs with timestamp, patient info, message, response, and escalation status
- **Session expiry** — sessions expire after 30 minutes of inactivity

---

## Tech Stack

- **Python** — core language
- **Flask** — web framework and session management
- **Anthropic Claude API** — `claude-opus-4-5` via the `anthropic` Python SDK
- **SQLite** — lightweight patient database
- **python-dotenv** — environment variable management
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

- **Multi-model support** — abstract the AI layer to support multiple LLM providers (OpenAI, Google Gemini, etc.)
- **Persistent session history** — store conversation history in the database so returning patients have continuity across sessions
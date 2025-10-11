NotifyHub — AI-Powered Appointment Confirmation System
->Overview

NotifyHub is an intelligent voice automation system that calls patients to confirm their upcoming appointments.
It integrates Google Sheets for appointment management and leverages AI-driven voice assistants to interact with patients in real time.

Over the course of development, NotifyHub evolved through five major versions, improving reliability, automation, and voice capabilities.
The current Version 5 integrates with Vapi.ai, providing a stable and scalable telephony solution for production use.
_________________________________________________________________________________________________________________________________________________

->Features

Automated Voice Calls: The assistant calls patients, introduces itself, confirms identity, and records attendance.

Google Sheets Integration: Reads and updates appointment data directly from a shared sheet.

Real-Time Updates: Automatically updates “Call Status” and “Appointment Confirmed” columns.

Webhook Integration: Connects Vapi.ai webhooks to your Flask server for real-time responses.

Error-Resilient Design: Handles failed calls and missing entries gracefully.

Customizable Conversation Flow: Modify the system prompt to fit different organizations (clinics, offices, events, etc.)
_________________________________________________________________________________________________________________________________________________

->Version History
Version 1(V1) — Local ChatGPT Integration
                Used OpenAI API directly to generate conversational responses.
                Calls were simulated locally using text input/output.
                No telephony integration yet.

Version 2(V2) — Twilio Integration Attempt
                Integrated Twilio for real phone calls.
                Used OpenAI API to drive conversation logic.
                Challenges: Real-time voice handling & latency.

Version 3(V3) — Custom FastAPI + WebSocket Version
                Shifted to FastAPI backend.
                Created internal voice flow logic and template-based prompt control.
                Introduced structured update_appointment_by_name() for Sheets automation.

Version 4(V4) — Stable Prototype (Local Voice Engine)
                Added end-to-end local testing using ngrok.
                Voice pipeline stable; however, call management was local only.
                Sheets automation working for local tests.

Version 5(V5) — Production Ready (Vapi Integration)
                Integrated Vapi.ai for real telephony and AI-driven voice calls.
                Assistant configured with system prompt and tool functions.
                Webhook system added for two-way updates with Sheets.
                Flask server handles POST webhook requests.
                Calls patients automatically and updates Sheets based on conversation outcomes.
_________________________________________________________________________________________________________________________________________________

->Architecture
Google Sheets  <-->  sheets_utils.py
                     ↑
                     │
Webhook (Flask)  <-->  webhook_server.py
                     ↑
                     │
Vapi.ai Assistant  <-->  vapi_utils.py
                     ↑
                     │
Caller Script  <-->  call_me.py
_________________________________________________________________________________________________________________________________________________

->Setup Instructions
1. Clone the Repository
   git clone https://github.com/<your-username>/NotifyHub.git
   cd NotifyHub

2. Create and Fill the .env File
   Add your credentials:

  VAPI_API_KEY=your_vapi_api_key
  VAPI_ASSISTANT_ID=your_vapi_assistant_id
  VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
  DEFAULT_COUNTRY_CODE=+91
  GOOGLE_SHEETS_ID=your_google_sheet_id

3. Add Service Account Credentials
   Place your Google service account key file in:
   credentials/service_account.json

4. Install Dependencies
   pip install -r requirements.txt

5. Run Flask Webhook Server
   python webhook_server.py

  Expose it via ngrok:
  ngrok http 5001
 
  Copy the ngrok HTTPS URL and add it as your Vapi Webhook URL in the assistant dashboard.

6. Start Calling Patients
   python call_me.py
_________________________________________________________________________________________________________________________________________________

->Google Sheets Format
Name	Phone	Date	Time	Status (Call)	Appointment Confirmed
Ram	7416743287	2025-08-08	10:00 PM	Called	Coming

Status (Call) — updated automatically when a call is made.

Appointment Confirmed — updated based on patient’s voice response.
_________________________________________________________________________________________________________________________________________________

->How It Works

call_me.py fetches the next pending patient from the sheet.

Calls the patient using the Vapi REST API.

Vapi’s AI assistant interacts with the patient using the system prompt.

On patient response, Vapi triggers a webhook → handled by webhook_server.py.

The webhook updates the correct row in Google Sheets.
_________________________________________________________________________________________________________________________________________________

-> Tech Stack

Python 3.10+

Flask (Webhook Server)

gspread + Google API

Vapi.ai (Voice Automation)

ngrok (Tunnel for webhook)

dotenv (Environment configuration)
_________________________________________________________________________________________________________________________________________________

->Future Enhancements

Real-time dashboard showing live call progress.

Multi-clinic configuration.

Voice transcription logging.

Multi-language support.

Integrating WhatsApp & SMS reminders.
_________________________________________________________________________________________________________________________________________________

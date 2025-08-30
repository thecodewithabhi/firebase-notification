import os
import time
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = 'fir-send-notification-e6a29' 
SERVICE_ACCOUNT_FILE = 'service-account.json'
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

if not PROJECT_ID:
    raise RuntimeError("PROJECT_ID is not set. Put it in .env")

# Prepare credentials
_creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Simple token cache
_token = None
_token_exp = 0

def get_access_token():
    global _token, _token_exp, _creds
    # refresh if missing or expiring within 60s
    if not _token or time.time() > (_token_exp - 60):
        _creds.refresh(Request())
        _token = _creds.token
        # google-auth sets expiry as datetime
        _token_exp = _creds.expiry.timestamp() if _creds.expiry else time.time() + 3000
    return _token

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return {"ok": True, "projectId": PROJECT_ID}

@app.route("/send", methods=["POST"])
def send():
    """
    Body JSON accepted:

    {
      "token": "<device_fcm_token>",         # OR
      "topic": "news",                       # choose one
      "title": "Hello",
      "body": "Message",
      "image": "https://example.com/img.png", # optional
      "data": {"k1":"v1","k2":"v2"}           # optional
    }
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    token = payload.get("token")
    topic = payload.get("topic")
    title = payload.get("title", "")
    body = payload.get("body", "")
    image = payload.get("image")
    data = payload.get("data", {})

    if not token and not topic:
        return jsonify({"error": "Provide either 'token' or 'topic'"}), 400

    # Build FCM v1 request
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json; UTF-8",
    }

    message = {
        "message": {
            "notification": {"title": title, "body": body},
            "data": {k: str(v) for k, v in (data or {}).items()}
        }
    }
    if image:
        message["message"]["notification"]["image"] = image
    if token:
        message["message"]["token"] = token
    else:
        message["message"]["topic"] = topic

    resp = requests.post(url, headers=headers, json=message)
    ok = 200 <= resp.status_code < 300

    return jsonify({
        "ok": ok,
        "status": resp.status_code,
        "fcm_response": (resp.json() if resp.text else None),
        "sent_to": ("token" if token else f"topic:{topic}")
    }), (200 if ok else 500)

if __name__ == "__main__":
    # Use 0.0.0.0 if you want to receive calls from outside your machine
    app.run(host="127.0.0.1", port=5000, debug=True)


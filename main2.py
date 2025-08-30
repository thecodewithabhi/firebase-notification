import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Path to your Firebase service account JSON file
SERVICE_ACCOUNT_FILE = 'service-account.json'

# Your Firebase project ID
PROJECT_ID = 'fir-send-notification-e6a29'

# Device token or topic to send the notification to
TARGET_TOKEN = 'target-device-token-or-topic'

# Notification payload
message_payload = {
    "message": {
        "token": TARGET_TOKEN,
        "notification": {
            "title": "Hello from Python!",
            "body": "This is a test push notification."
        }
    }
}

def get_access_token():
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    credentials.refresh(Request())
    return credentials.token

def send_fcm_message():
    access_token = get_access_token()
    url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; UTF-8',
    }

    response = requests.post(url, headers=headers, data=json.dumps(message_payload))

    if response.status_code == 200:
        print('Notification sent successfully:', response.json())
    else:
        print('Error sending notification:', response.status_code, response.text)

if __name__ == '__main__':
    send_fcm_message()


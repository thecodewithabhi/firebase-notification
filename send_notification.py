import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Step 1: Configure Firebase Settings
SERVICE_ACCOUNT_FILE = 'service-account.json'  # Path to your downloaded service account file
PROJECT_ID = 'fir-send-notification-e6a29'              # Your Firebase Project ID (from Firebase Console)
DEVICE_TOKEN = 'fPaMkdRcEwuPuVTaT8XsaK:APA91bHO6IphE_txNRIiPNPIPFvkz8c9fVS63phOQibHFHrDPLPATu2Jjx7nvg7QHmBbi0UHVDBUoaEkW76BRzlKWqm0ZjlBxePpdYkiPIpK15El6AUy6Uo'  # Device token

# Step 2: Prepare the message payload
message_payload = {
    "message": {
        "token": DEVICE_TOKEN,
        "notification": {
            "title": "Hello from Python!",  # Notification title
            "body": "This is a push notification via FCM HTTP v1 API"  # Notification body
        }
    }
}

# Step 3: Function to get an OAuth2 access token
def get_access_token():
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    credentials.refresh(Request())
    return credentials.token

# Step 4: Send the notification via Firebase Cloud Messaging (FCM)
def send_notification():
    try:
        access_token = get_access_token()  # Get the access token
        url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

        # Set the request headers with Authorization (Bearer token) and Content-Type
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        # Send the POST request with the message payload
        response = requests.post(url, headers=headers, data=json.dumps(message_payload))

        # Check the response
        if response.status_code == 200:
            print('✅ Notification sent successfully:', response.json())
            print(response.text)
        else:
            print(f'❌ Failed to send notification [{response.status_code}]: {response.text}')

    except Exception as e:
        print(f'❌ Error occurred while sending notification: {e}')

if __name__ == '__main__':
    send_notification()

import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Step 1: Configure
SERVICE_ACCOUNT_FILE = 'service-account.json'
PROJECT_ID = 'fir-send-notification-6eA29'
DEVICE_TOKEN = 'fPaMkdRcEwuPuVTaT8XsaK:APA91bHO6IphE_txNRIiPNPIPFvkz8c9fVS63phOQibHFHrDPLPATu2Jjx7nvg7QHmBbi0UHVDBUoaEkW76BRzlKWqm0ZjlBxePpdYkiPIpK15El6AUy6Uo'             # From your app

# Prepare Firebase Authentication
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
auth_request = Request()

# Prepare Firebase Cloud Messaging endpoint
url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

# Directus API request to get the title and body
directus_url = 'https://firebase-notification.directus.app'
collection_name = 'notification'
headers_directus = {"Authorization": "Bearer 4gFa5biODkz2vhkvnwCxgFl3fmelhXBO"}
response = requests.get(f"{directus_url}/items/{collection_name}", headers=headers_directus)
if response.status_code == 200:
    data = response.json()
    title = data['data'][0]['title']
    body = data['data'][0]['message']

    # Step 2: Prepare the Firebase message payload
    message_payload = {
        "message": {
            "token": DEVICE_TOKEN,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    # Send the notification
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    firebase_response = requests.post(url, headers=headers, json=message_payload)

    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code}")
else:
    print(f"Error fetching data from Directus: {response.status_code}")

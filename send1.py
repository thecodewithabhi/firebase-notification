import os
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Step 1: Firebase Setup
SERVICE_ACCOUNT_FILE = 'service-account.json'
PROJECT_ID = 'fir-send-notification-e6a29'

# Prepare Firebase Authentication
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
credentials.refresh(Request())  # ✅ refresh token

# Firebase endpoint
url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

# Step 2: Directus API setup
directus_url = 'https://firebase-notification.directus.app'
collection_name = 'notification'

# 🔑 Load token (either directly or from env variable)
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "4gFa5biODkz2vhkvnwCxgFl3fmelhXBO")
headers_directus = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

response = requests.get(f'{directus_url}/items/{collection_name}', headers=headers_directus)
print(response.text)
if response.status_code == 200:
    data = response.json()
    if not data["data"]:
        print("⚠️ No notifications found in Directus.")
        exit()

    # Take the latest notification
    notification = data['data'][-1]   
    title = notification.get('title', 'No Title')
    body = notification.get('message', 'No Message')
    target = notification.get('target', '')

    # Step 3: Prepare Firebase payload
    message_payload = {
        "message": {
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    if target.startswith("APA91"):  
        message_payload["message"]["token"] = target
    else:
        message_payload["message"]["topic"] = target

    # Step 4: Send Notification
    headers_firebase = {
        'Authorization': f'Bearer {credentials.token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers_firebase, json=message_payload)

    if response.status_code == 200:
        print("✅ Notification sent successfully!")
        print(response.json())
    else:
        print(f"❌ Failed to send notification: {response.status_code}")
        print(response.text)

else:
    print(f"❌ Error fetching data from Directus: {response.status_code}")
    print(response.text)

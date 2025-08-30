import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# =============== STEP 1: Firebase Setup ===============
SERVICE_ACCOUNT_FILE = 'service-account.json'  # Path to your service account JSON
PROJECT_ID = 'fir-send-notification-e6a29'

# Authenticate with Firebase
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
credentials.refresh(Request())  # Refresh token

# Firebase endpoint
firebase_url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

# =============== STEP 2: Directus Setup ===============
directus_url = "https://firebase-notification.directus.app"
collection_name = "notification"

# Directus API Key (make sure it's a Bearer token)
headers_directus = {"Authorization": "Bearer 4gFa5biODkz2vhkvnwCxgFl3fmelhXBO"}

# Fetch latest notification
response = requests.get(f"{directus_url}/items/{collection_name}", headers=headers_directus)

if response.status_code == 200:
    data = response.json().get("data", [])
    
    if not data:
        print("⚠️ No notifications found in Directus.")
        exit()

    # Take latest notification (last one)
    notification = data[-1]
    title = notification.get("title", "No Title")
    body = notification.get("message", "No Message")
    target = notification.get("target", "")

    print(f"✅ Fetched from Directus -> Title: {title}, Message: {body}, Target: {target}")

    # =============== STEP 3: Build Firebase Message ===============
    message_payload = {
        "message": {
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    # If target looks like a device token
    if target.startswith("APA91"):
        message_payload["message"]["token"] = target
    else:
        # Assume it's a topic
        message_payload["message"]["topic"] = target

    # =============== STEP 4: Send Notification ===============
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    firebase_response = requests.post(firebase_url, headers=headers, json=message_payload)

    if firebase_response.status_code == 200:
        print("✅ Notification sent successfully!")
        print(firebase_response.json())
    else:
        print(f"❌ Failed to send notification: {firebase_response.status_code}")
        print(firebase_response.text)

else:
    print(f"❌ Error fetching data from Directus: {response.status_code}")
    print(response.text)

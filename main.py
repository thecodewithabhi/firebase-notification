import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate('firebase/service-account.json')
firebase_admin.initialize_app(cred)

def send_notification_to_topic(title, body, topic='news'):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic,
    )
    response = messaging.send(message)
    print("Notification sent:", response)

# Example usage
send_notification_to_topic("Hello!", "This is a message from Directus payload")

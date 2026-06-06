import logging
import firebase_admin
from firebase_admin import messaging

logger = logging.getLogger(__name__)

def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    """
    Sends a push notification via FCM.
    In a real app, you would look up the user's FCM device token from MongoDB.
    For this mock implementation, we just log it to the console.
    """
    try:
        # Mocking the FCM token lookup
        mock_device_token = "mock_fcm_token_123"
        
        # If firebase is actually initialized, we can attempt to construct a message
        # But we won't send it unless we have a real token
        if firebase_admin._apps:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=mock_device_token,
            )
            # messaging.send(message) # Commented out to prevent errors with fake tokens
            
        logger.info(f"==> PUSH NOTIFICATION SENT to {user_id}: {title} | {body}")
        return True
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False

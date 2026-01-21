import firebase_admin
from firebase_admin import credentials, auth, firestore
from .config import settings
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    if not firebase_admin._apps:
        # Check if credentials file exists
        if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
            cred = credentials.Certificate(settings.google_application_credentials)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
            })
        else:
            # Use default credentials (works in GCP environment)
            firebase_admin.initialize_app()

# Get Firestore client
def get_firestore_client():
    if not firebase_admin._apps:
        initialize_firebase()
    return firestore.client()

# Verify Firebase ID token
def verify_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        return None

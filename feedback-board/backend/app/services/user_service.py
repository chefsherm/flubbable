from google.cloud.firestore import Client
from ..core.config import settings


class UserService:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection('users')

    def get_or_create_user(self, uid: str, email: str) -> dict:
        """Get user from Firestore or create if doesn't exist"""
        user_ref = self.collection.document(uid)
        user_doc = user_ref.get()

        if user_doc.exists:
            return {'uid': uid, **user_doc.to_dict()}

        # Check if this is the first user (make them admin)
        all_users = list(self.collection.limit(1).stream())
        is_admin = len(all_users) == 0

        # Also check if email matches admin email from settings
        if settings.admin_email and email == settings.admin_email:
            is_admin = True

        # Create new user
        user_data = {
            'email': email,
            'is_admin': is_admin,
            'created_at': self.db.SERVER_TIMESTAMP,
        }

        user_ref.set(user_data)

        # Fetch the created user to get the timestamp
        user_doc = user_ref.get()
        return {'uid': uid, **user_doc.to_dict()}

    def get_user(self, uid: str) -> dict:
        """Get user by UID"""
        user_ref = self.collection.document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return None

        return {'uid': uid, **user_doc.to_dict()}

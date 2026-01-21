from google.cloud.firestore import Client
from typing import List, Optional
from datetime import datetime


class FeatureRequestService:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection('feature_requests')

    def create(self, title: str, description: str, author_id: str, author_email: str) -> dict:
        """Create a new feature request"""
        request_data = {
            'title': title,
            'description': description,
            'author_id': author_id,
            'author_email': author_email,
            'votes': 0,
            'created_at': self.db.SERVER_TIMESTAMP,
            'updated_at': self.db.SERVER_TIMESTAMP,
        }

        doc_ref = self.collection.add(request_data)
        request_id = doc_ref[1].id

        # Fetch the created document to get server timestamps
        created_doc = self.collection.document(request_id).get()
        return {'id': request_id, **created_doc.to_dict()}

    def get_all(self) -> List[dict]:
        """Get all feature requests"""
        docs = self.collection.order_by('created_at', direction='DESCENDING').stream()
        requests = []

        for doc in docs:
            data = doc.to_dict()
            # Convert timestamps to ISO format strings
            if data.get('created_at'):
                data['created_at'] = data['created_at'].isoformat()
            if data.get('updated_at'):
                data['updated_at'] = data['updated_at'].isoformat()
            requests.append({'id': doc.id, **data})

        return requests

    def get_by_id(self, request_id: str) -> Optional[dict]:
        """Get a feature request by ID"""
        doc = self.collection.document(request_id).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        # Convert timestamps
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()
        if data.get('updated_at'):
            data['updated_at'] = data['updated_at'].isoformat()

        return {'id': doc.id, **data}

    def delete(self, request_id: str) -> bool:
        """Delete a feature request and all its votes"""
        # Delete all votes for this request
        votes_ref = self.db.collection('votes')
        votes = votes_ref.where('request_id', '==', request_id).stream()

        for vote in votes:
            vote.reference.delete()

        # Delete the request
        self.collection.document(request_id).delete()
        return True

    def increment_votes(self, request_id: str) -> dict:
        """Increment vote count"""
        doc_ref = self.collection.document(request_id)
        doc_ref.update({
            'votes': firestore.Increment(1),
            'updated_at': self.db.SERVER_TIMESTAMP
        })

        # Return updated document
        return self.get_by_id(request_id)

    def decrement_votes(self, request_id: str) -> dict:
        """Decrement vote count"""
        doc_ref = self.collection.document(request_id)
        doc_ref.update({
            'votes': firestore.Increment(-1),
            'updated_at': self.db.SERVER_TIMESTAMP
        })

        # Return updated document
        return self.get_by_id(request_id)


# Import at the end to avoid circular imports
from google.cloud import firestore

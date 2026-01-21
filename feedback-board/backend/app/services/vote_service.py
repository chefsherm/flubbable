from google.cloud.firestore import Client
from typing import List, Optional


class VoteService:
    def __init__(self, db: Client):
        self.db = db
        self.collection = db.collection('votes')

    def create_vote(self, user_id: str, request_id: str) -> dict:
        """Create a vote for a feature request"""
        # Check if user already voted
        existing_vote = self.get_user_vote(user_id, request_id)
        if existing_vote:
            return existing_vote

        vote_data = {
            'user_id': user_id,
            'request_id': request_id,
            'created_at': self.db.SERVER_TIMESTAMP,
        }

        doc_ref = self.collection.add(vote_data)
        vote_id = doc_ref[1].id

        # Fetch the created vote
        created_doc = self.collection.document(vote_id).get()
        data = created_doc.to_dict()

        # Convert timestamp
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()

        return {'id': vote_id, **data}

    def delete_vote(self, user_id: str, request_id: str) -> bool:
        """Delete a user's vote for a feature request"""
        votes = self.collection.where('user_id', '==', user_id).where('request_id', '==', request_id).stream()

        deleted = False
        for vote in votes:
            vote.reference.delete()
            deleted = True

        return deleted

    def get_user_vote(self, user_id: str, request_id: str) -> Optional[dict]:
        """Get a user's vote for a specific request"""
        votes = list(self.collection.where('user_id', '==', user_id).where('request_id', '==', request_id).limit(1).stream())

        if not votes:
            return None

        vote = votes[0]
        data = vote.to_dict()

        # Convert timestamp
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()

        return {'id': vote.id, **data}

    def get_user_votes(self, user_id: str) -> List[dict]:
        """Get all votes by a user"""
        votes = self.collection.where('user_id', '==', user_id).stream()
        result = []

        for vote in votes:
            data = vote.to_dict()
            # Convert timestamp
            if data.get('created_at'):
                data['created_at'] = data['created_at'].isoformat()
            result.append({'id': vote.id, **data})

        return result

    def has_user_voted(self, user_id: str, request_id: str) -> bool:
        """Check if user has voted for a request"""
        return self.get_user_vote(user_id, request_id) is not None

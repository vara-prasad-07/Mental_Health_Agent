import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import json

firebase_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not firebase_json:
    raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON is not set in environment")
    
class FirestoreClient:
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Path to your service account key file
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore client
        self.db = firestore.client()
    
    def get_user_data(self, uid: str) -> Optional[Dict[str, Any]]:
        try:
            # Reference to the user document
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                # Add the document ID to the response
                user_data['uid'] = uid
                formatted_response = {
                    "workoutHistory": user_data.get('workoutHistory', []),
                    "DietLogs": user_data.get('meals', {}),
                    "waterLogs": user_data.get('waterLogs', []),
                    "basicInfo": {
                        "displayName": user_data.get('displayName', ''),
                        "email": user_data.get('email', ''),
                        "level": user_data.get('level', 1),
                        "dietCalories": user_data.get('dietCalories', 0),
                        "dietGoalMet": user_data.get('dietGoalMet', False)
                    }
                }
                return formatted_response
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching user data for uid {uid}: {str(e)}")
            raise e
    
    def get_or_create_session(self, uid: str, session_id: str) -> Dict[str, Any]:
        """
        Get existing session or create new one within the user document
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                sessions = user_data.get('sessions', {})
                
                if session_id in sessions:
                    return sessions[session_id]
                else:
                    # Create new session
                    new_session = {
                        "session_id": session_id,
                        "created_at": datetime.utcnow(),
                        "messages": [],
                        "dataFetched": False,
                        "userData": {}
                    }
                    sessions[session_id] = new_session
                    user_ref.update({'sessions': sessions})
                    return new_session
            else:
                raise Exception(f"User {uid} not found")
                
        except Exception as e:
            print(f"Error getting/creating session for uid {uid}, session {session_id}: {str(e)}")
            raise e
    
    def update_session(self, uid: str, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Update session data within the user document
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                sessions = user_data.get('sessions', {})
                sessions[session_id] = session_data
                user_ref.update({'sessions': sessions})
                return True
            else:
                raise Exception(f"User {uid} not found")
            
        except Exception as e:
            print(f"Error updating session for uid {uid}, session {session_id}: {str(e)}")
            raise e
    
    def get_all_user_sessions(self, uid: str) -> Dict[str, Any]:
        """
        Get all sessions for a user
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return user_data.get('sessions', {})
            else:
                return {}
                
        except Exception as e:
            print(f"Error fetching sessions for uid {uid}: {str(e)}")
            raise e
    
    def delete_session(self, uid: str, session_id: str) -> bool:
        """
        Delete a specific session from user document
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                sessions = user_data.get('sessions', {})
                if session_id in sessions:
                    del sessions[session_id]
                    user_ref.update({'sessions': sessions})
                    return True
            return False
            
        except Exception as e:
            print(f"Error deleting session for uid {uid}, session {session_id}: {str(e)}")
            raise e



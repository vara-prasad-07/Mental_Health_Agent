from fastapi import FastAPI, HTTPException, Query
from llm import LLM
from data import FirestoreClient
from uuid import uuid4
from datetime import datetime
import os
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://mental-health-agent-0oib.onrender.com",  
    "https://your-frontend-domain.com",               
    "http://localhost:3000",                         
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)

llm = LLM()
firestore_client = FirestoreClient()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/query/{uid}")
async def mental_health_chat(uid: str, query: str = Query(..., description="User's mental health query"), session_id: str = Query(default=None, description="Session ID for conversation continuity")):
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())
        
        # Get or create session
        session_data = firestore_client.get_or_create_session(uid, session_id)
        
        # Fetch user data if not already fetched
        user_data = None
        if not session_data.get("dataFetched", False):
            user_data = firestore_client.get_user_data(uid)
            if user_data:
                # Update session with user data
                session_data["userData"] = user_data
                session_data["dataFetched"] = True
                firestore_client.update_session(uid, session_id, session_data)
        else:
            # Use cached user data from session
            user_data = session_data.get("userData", {})
        
        # Get conversation history
        conversation_history = session_data.get("messages", [])
        
        # Generate AI response using LLM with context
        ai_response = llm.generate_content(
            contents=query,
            user_data=user_data,
            conversation_history=conversation_history
        )
        
        # Create message entry
        new_message = {
            "role": "user",
            "query": query,
            "assistant": "mental_health_ai",
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add message to session
        session_data["messages"].append(new_message)
        
        # Update session in Firestore
        firestore_client.update_session(uid, session_id, session_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "response": ai_response,
            "conversation_length": len(session_data["messages"]),
            "data_fetched": session_data.get("dataFetched", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.get("/sessions/{uid}")
async def get_all_sessions(uid: str):
    """
    Get all sessions for a user
    """
    try:
        sessions = firestore_client.get_all_user_sessions(uid)
        
        # Format sessions for response
        session_list = []
        for session_id, session_data in sessions.items():
            session_list.append({
                "session_id": session_id,
                "created_at": session_data.get("created_at"),
                "messages": session_data.get("messages", []),
                "message_count": len(session_data.get("messages", [])),
                "data_fetched": session_data.get("dataFetched", False),
                "last_message": session_data.get("messages", [])[-1] if session_data.get("messages") else None
            })
        
        return {
            "success": True,
            "uid": uid,
            "session_count": len(session_list),
            "sessions": session_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")





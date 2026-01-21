from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.firebase import initialize_firebase
from .api import users, feature_requests, votes
from .services.agent_websocket import handle_websocket
import uuid

# Initialize Firebase on startup
initialize_firebase()

app = FastAPI(
    title="Feedback Board API",
    description="API for managing feature requests and votes",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(feature_requests.router)
app.include_router(votes.router)


@app.get("/")
async def root():
    return {
        "message": "Feedback Board API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/agent")
async def websocket_agent_endpoint(websocket: WebSocket):
    """WebSocket endpoint for AI agent communication"""
    client_id = str(uuid.uuid4())
    await handle_websocket(websocket, client_id)

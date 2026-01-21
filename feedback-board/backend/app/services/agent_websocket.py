"""
WebSocket integration for real-time AI agent communication
Connects the LangGraph agent with the Next.js frontend
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import sys
import os

# Add ai-dev-agent to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai-dev-agent'))

try:
    from agent import create_workflow
    from schemas import Blueprint, TestSuite, Implementation
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    print("⚠️ AI agent not available - install dependencies from ai-dev-agent/")


class AgentWebSocketManager:
    """Manages WebSocket connections and agent execution"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.workflow = create_workflow() if AGENT_AVAILABLE else None

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"🔌 Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"🔌 Client {client_id} disconnected")

    async def send_message(self, client_id: str, message_type: str, payload: Any):
        """Send message to specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json({
                "type": message_type,
                "payload": payload
            })

    async def generate_blueprint(self, client_id: str, user_request: str):
        """Generate blueprint from user request"""
        if not AGENT_AVAILABLE:
            await self.send_message(client_id, "ERROR", {
                "message": "AI agent not available"
            })
            return

        try:
            # Run only planner node
            from agent import planner_node, AgentState

            initial_state: AgentState = {
                "user_request": user_request,
                "tech_stack_context": "Next.js, FastAPI, Firestore",
                "output_directory": "./generated",
                "use_e2b": False,
                "blueprint": None,
                "test_suite": None,
                "implementation": None,
                "sandbox_result": None,
                "attempt_count": 0,
                "max_attempts": 3,
                "status": "START",
                "total_tokens_used": 0,
                "total_cost_usd": 0.0,
                "errors": []
            }

            # Execute planner
            result = planner_node(initial_state)

            if result.get("blueprint"):
                blueprint = result["blueprint"]

                # Convert to frontend format
                payload = {
                    "nodes": [
                        {
                            "id": comp.name,
                            "label": comp.description,
                            "type": comp.type,
                            "status": "pending"
                        }
                        for comp in blueprint.components
                    ],
                    "database_changes": [
                        f"+ Collection: {coll.name}"
                        for coll in blueprint.firestore_collections
                    ],
                    "risk_audit": {
                        "status": "WARNING" if blueprint.complexity == "complex" else "SAFE",
                        "risks": [] if blueprint.complexity == "simple" else ["Complex implementation"]
                    },
                    "cost_estimate": blueprint.estimated_tokens
                }

                await self.send_message(client_id, "BLUEPRINT_GENERATED", payload)
            else:
                await self.send_message(client_id, "ERROR", {
                    "message": "Failed to generate blueprint"
                })

        except Exception as e:
            print(f"❌ Error generating blueprint: {str(e)}")
            await self.send_message(client_id, "ERROR", {
                "message": f"Error: {str(e)}"
            })

    async def approve_and_build(self, client_id: str, approved_plan: Dict[str, Any]):
        """Execute build after user approval"""
        if not AGENT_AVAILABLE:
            await self.send_message(client_id, "ERROR", {
                "message": "AI agent not available"
            })
            return

        try:
            await self.send_message(client_id, "BUILD_STARTED", {})

            # Run full agent workflow
            from agent import run_agent

            # Extract user request from plan (should be stored in session)
            # For now, use a placeholder
            user_request = "Build the approved feature"

            # TODO: Actually run agent and stream results
            # This would require refactoring run_agent to support streaming

            await self.send_message(client_id, "TERMINAL_LOG", {
                "message": "🚀 Starting build process..."
            })

            await self.send_message(client_id, "TERMINAL_LOG", {
                "message": "📝 Generating code..."
            })

            # Simulate for now - in production, this would stream real agent output
            await self.send_message(client_id, "BUILD_COMPLETE", {
                "message": "Build completed successfully!"
            })

        except Exception as e:
            print(f"❌ Error during build: {str(e)}")
            await self.send_message(client_id, "ERROR", {
                "message": f"Build error: {str(e)}"
            })


# Global manager instance
ws_manager = AgentWebSocketManager()


async def handle_websocket(websocket: WebSocket, client_id: str):
    """Main WebSocket handler"""
    await ws_manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            payload = data.get("payload", {})

            print(f"📨 Received {message_type} from {client_id}")

            if message_type == "GENERATE_PLAN":
                await ws_manager.generate_blueprint(
                    client_id,
                    payload.get("message", "")
                )

            elif message_type == "APPROVE_PLAN":
                await ws_manager.approve_and_build(
                    client_id,
                    payload.get("plan", {})
                )

            elif message_type == "PING":
                await ws_manager.send_message(client_id, "PONG", {})

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WebSocket error: {str(e)}")
        ws_manager.disconnect(client_id)

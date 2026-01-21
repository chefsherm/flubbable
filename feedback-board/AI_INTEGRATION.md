# AI-Powered Blueprint Integration

This document explains the AI agent integration that transforms the feedback board into an AI-powered development platform.

## 🎯 Overview

Users can now interact with an AI agent to:
1. **Describe features** in natural language
2. **Review AI-generated blueprints** with architecture visualization
3. **Approve blueprints** for automatic implementation
4. **Watch real-time build progress** in a terminal-like interface

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│                                                             │
│  ┌──────────────┐           ┌──────────────────┐          │
│  │ ChatInterface│◄─────────►│  BlueprintView    │          │
│  │              │           │                   │          │
│  │ - User input │           │ - Architecture    │          │
│  │ - Chat history│           │ - DB changes     │          │
│  └──────┬───────┘           │ - Risk audit     │          │
│         │                    │ - Approve button │          │
│         │                    └─────────┬────────┘          │
│         │                              │                   │
│         │        ┌────────────────────┐│                   │
│         │        │  TerminalView      ││                   │
│         │        │                    ││                   │
│         │        │  - Live logs       ││                   │
│         │        │  - Build status    ││                   │
│         │        └────────────────────┘│                   │
│         │                              │                   │
│         └──────────────┬───────────────┘                   │
│                        │                                   │
│                  ┌─────▼──────┐                            │
│                  │ useAgent   │ WebSocket Hook             │
│                  │  Hook      │                            │
│                  └─────┬──────┘                            │
└────────────────────────┼────────────────────────────────────┘
                         │ WebSocket (/ws/agent)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Backend (FastAPI)                           │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │     AgentWebSocketManager                    │          │
│  │                                              │          │
│  │  • handle_websocket()                       │          │
│  │  • generate_blueprint()                     │          │
│  │  • approve_and_build()                      │          │
│  └────────────────┬──────────────────────────────┘          │
│                   │                                         │
│         ┌─────────▼──────────┐                             │
│         │   LangGraph Agent   │                             │
│         │                     │                             │
│         │  • planner_node     │                             │
│         │  • verifier_node    │                             │
│         │  • builder_node     │                             │
│         │  • sandbox_node     │                             │
│         └─────────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

### Backend

```
feedback-board/backend/app/
├── services/
│   └── agent_websocket.py      # WebSocket manager + AI integration
└── main.py                     # WebSocket endpoint (/ws/agent)
```

### Frontend

```
feedback-board/frontend/src/
├── app/
│   └── ai-agent/
│       └── page.tsx            # Main AI agent page
├── components/
│   └── Blueprint/
│       ├── ChatInterface.tsx   # Chat UI
│       ├── BlueprintView.tsx   # Blueprint approval UI
│       ├── ArchitectureGraph.tsx # Visual component graph
│       ├── DatabaseDiff.tsx    # DB changes viewer
│       └── TerminalView.tsx    # Build logs terminal
├── hooks/
│   └── useAgent.ts             # WebSocket hook
└── store/
    └── blueprintStore.ts       # Zustand state management
```

## 🔄 Workflow

### 1. User Describes Feature

User types in ChatInterface:
```
"Create a user profile page with avatar upload"
```

Message sent via WebSocket:
```json
{
  "type": "GENERATE_PLAN",
  "payload": {
    "message": "Create a user profile page with avatar upload"
  }
}
```

### 2. AI Generates Blueprint

Backend executes `planner_node()` from LangGraph agent:
```python
result = planner_node(initial_state)
blueprint = result["blueprint"]
```

Blueprint sent back via WebSocket:
```json
{
  "type": "BLUEPRINT_GENERATED",
  "payload": {
    "nodes": [
      {
        "id": "ProfilePage",
        "label": "User profile page component",
        "type": "frontend",
        "status": "pending"
      },
      {
        "id": "upload_endpoint",
        "label": "Avatar upload API",
        "type": "backend",
        "status": "pending"
      }
    ],
    "database_changes": [
      "+ Collection: user_profiles"
    ],
    "risk_audit": {
      "status": "SAFE",
      "risks": []
    },
    "cost_estimate": 2500
  }
}
```

### 3. User Reviews Blueprint

`BlueprintView` renders:
- **Architecture Graph**: Visual component layout
- **Database Changes**: Firestore collections to be created
- **Risk Assessment**: Safety checks
- **Cost Estimate**: Token usage estimate

### 4. User Approves

User clicks "Approve & Build" button:

```typescript
approveBuild(plan);
```

Message sent via WebSocket:
```json
{
  "type": "APPROVE_PLAN",
  "payload": {
    "plan": { /* full blueprint */ }
  }
}
```

### 5. AI Builds Feature

Backend responds:
```json
{
  "type": "BUILD_STARTED"
}
```

Frontend switches to `TerminalView` and streams logs:

```
🚀 Starting build process...
📝 Generating code...
🧪 Running tests...
✅ Build completed successfully!
```

## 🎨 UI Components

### ChatInterface

- Left panel with chat history
- Connection status indicator
- Input form for feature requests
- Example prompts for quick start

### BlueprintView

Three modes:
1. **Empty State**: Waiting for blueprint
2. **Blueprint Review**: Show architecture, DB changes, risks
3. **Terminal**: Build progress logs

### ArchitectureGraph

Visual representation of components grouped by layer:
- Frontend Layer (blue)
- Backend Layer (purple)
- Database Layer (green)

### DatabaseDiff

Shows Firestore changes with diff-style formatting:
- `+` Green: New collections
- `-` Red: Removed collections
- `~` Yellow: Modified collections

### TerminalView

macOS-style terminal with:
- Traffic light window controls
- Auto-scrolling logs
- Status indicator (Building/Complete)
- "Start New" button when done

## 🔧 WebSocket API

### Client → Server Messages

#### Generate Plan
```json
{
  "type": "GENERATE_PLAN",
  "payload": {
    "message": "Feature description here"
  }
}
```

#### Approve Plan
```json
{
  "type": "APPROVE_PLAN",
  "payload": {
    "plan": { /* blueprint object */ }
  }
}
```

#### Ping (Keepalive)
```json
{
  "type": "PING"
}
```

### Server → Client Messages

#### Blueprint Generated
```json
{
  "type": "BLUEPRINT_GENERATED",
  "payload": { /* blueprint */ }
}
```

#### Build Started
```json
{
  "type": "BUILD_STARTED",
  "payload": {}
}
```

#### Terminal Log
```json
{
  "type": "TERMINAL_LOG",
  "payload": {
    "message": "Log message here"
  }
}
```

#### Build Complete
```json
{
  "type": "BUILD_COMPLETE",
  "payload": {
    "message": "Build completed successfully!"
  }
}
```

#### Error
```json
{
  "type": "ERROR",
  "payload": {
    "message": "Error description"
  }
}
```

## 🚀 Running the Integration

### Prerequisites

1. **Backend AI agent** must be available:
```bash
cd feedback-board/backend
# AI agent code should be accessible at ../ai-dev-agent/
```

2. **Install dependencies**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Start Services

**Terminal 1 - Backend:**
```bash
cd feedback-board/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd feedback-board/frontend
npm run dev
```

### Access AI Agent

Visit: **http://localhost:3000/ai-agent**

## 🎯 Usage Examples

### Example 1: Simple Feature

**User Input:**
```
Create a contact form with name, email, and message fields
```

**Blueprint Generated:**
- ContactForm component (frontend)
- /api/contact endpoint (backend)
- contacts collection (database)

**User Action:** Click "Approve & Build"

**AI Action:** Generates code, runs tests, reports success

### Example 2: Complex Feature

**User Input:**
```
Add user authentication with Google OAuth and session management
```

**Blueprint Generated:**
- LoginButton component
- GoogleAuth component
- /api/auth/google endpoint
- /api/auth/session endpoint
- users collection
- sessions collection

**Risk Audit:** ⚠️ WARNING - Complex authentication flow

**User Action:** Reviews risks, clicks "Approve & Build"

## 🔒 Security Considerations

### Authentication

Currently, WebSocket connections are **not authenticated**. For production:

```python
@app.websocket("/ws/agent")
async def websocket_agent_endpoint(
    websocket: WebSocket,
    current_user: dict = Depends(get_current_user)  # Add auth
):
    # Verify user has permission to use AI agent
    if not current_user.get('is_admin'):
        await websocket.close(code=403)
        return

    await handle_websocket(websocket, current_user['uid'])
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.websocket("/ws/agent")
@limiter.limit("10/hour")  # 10 blueprint generations per hour
async def websocket_agent_endpoint(...):
    ...
```

### Input Validation

Sanitize user inputs before sending to AI:

```python
def sanitize_user_input(text: str) -> str:
    # Remove potential injection attacks
    # Limit length
    # Filter inappropriate content
    return text[:2000].strip()
```

## 🐛 Troubleshooting

### WebSocket Won't Connect

**Problem:** Frontend shows "Disconnected"

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/app/core/config.py`
3. Verify WS URL in frontend `.env.local`

### AI Agent Not Available

**Problem:** Backend logs show "⚠️ AI agent not available"

**Solution:**
```bash
cd feedback-board/backend
pip install -r ../../ai-dev-agent/requirements.txt
```

### Blueprint Not Rendering

**Problem:** Chat works but blueprint doesn't appear

**Solutions:**
1. Check browser console for errors
2. Verify Zustand store is updating: React DevTools
3. Check WebSocket messages in Network tab

## 📈 Future Enhancements

- [ ] **Authentication**: Secure WebSocket connections
- [ ] **History**: Save past blueprints in Firestore
- [ ] **Collaboration**: Multiple users reviewing same blueprint
- [ ] **Git Integration**: Auto-commit generated code
- [ ] **Code Preview**: Show generated code before building
- [ ] **Rollback**: Undo/revert builds
- [ ] **Notifications**: Email when build completes
- [ ] **Analytics**: Track blueprint acceptance rate

## 📝 License

MIT

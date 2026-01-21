# Feedback Board - AI-Powered Micro-SaaS

A full-stack feedback board application where users can post feature requests, vote on ideas, and admins can manage submissions. **Now with AI-powered feature development!**

## Features

### Core Features
- 🔐 **Authentication** - Firebase Authentication (email/password)
- 📝 **Feature Requests** - Users can create and view feature requests
- ⬆️ **Voting System** - Upvote/downvote feature requests
- 👑 **Admin Controls** - Admins can delete any post
- 🎨 **Modern UI** - Built with Next.js, Tailwind CSS, and Mantine
- 🚀 **Fast API** - Python FastAPI backend
- 💾 **Cloud Database** - Google Cloud Firestore

### 🤖 AI-Powered Development (NEW!)
- **Natural Language to Blueprint** - Describe features in plain English, get technical blueprints
- **Visual Architecture** - See component graphs, database changes, and risk assessments
- **Human-in-the-Loop** - Review and approve AI-generated plans before implementation
- **Real-time Build Monitoring** - Watch AI implement features with live terminal logs
- **WebSocket Integration** - Real-time communication between frontend and AI agent
- **LangGraph Agent** - Powered by Claude Sonnet 4 for intelligent code generation

> Visit `/ai-agent` to interact with the AI development assistant!

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand + TanStack Query
- **Authentication**: Firebase Auth
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Database**: Google Cloud Firestore
- **Authentication**: Firebase Admin SDK
- **Server**: Uvicorn

### Infrastructure
- **Containerization**: Docker
- **Cloud Provider**: Google Cloud Platform (GCP)
- **Database**: Cloud Firestore

## Project Structure

```
feedback-board/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities and configurations
│   │   ├── store/           # Zustand state stores
│   │   └── types/           # TypeScript type definitions
│   ├── package.json
│   └── tsconfig.json
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Core configurations
│   │   ├── models/          # Pydantic models
│   │   └── services/        # Business logic services
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml        # Docker orchestration
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose (optional, for containerized setup)
- Firebase project with Firestore enabled
- Google Cloud Platform account

## Setup Instructions

### 1. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable **Authentication** → Email/Password provider
4. Enable **Firestore Database** → Start in production mode
5. Go to Project Settings → Service Accounts
6. Click "Generate new private key" and save the JSON file
7. Copy the Firebase config from Project Settings → General → Your apps

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `backend/.env`:
```env
FIREBASE_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
ADMIN_EMAIL=admin@example.com  # First user with this email becomes admin
```

Place your Firebase service account JSON file in the backend directory and update the path in `.env`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:
```env
# Get these values from Firebase Console → Project Settings → General
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Option 1: Run Locally (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

### Option 2: Docker Compose

```bash
# From the feedback-board directory
docker-compose up --build
```

Visit: http://localhost:3000

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- All protected endpoints require `Authorization: Bearer <firebase-token>` header

#### Feature Requests
- `GET /feature-requests` - Get all feature requests (public)
- `GET /feature-requests/{id}` - Get specific request (public)
- `POST /feature-requests` - Create new request (authenticated)
- `DELETE /feature-requests/{id}` - Delete request (admin only)
- `POST /feature-requests/{id}/vote` - Vote for request (authenticated)
- `DELETE /feature-requests/{id}/vote` - Remove vote (authenticated)

#### Users
- `GET /users/me` - Get current user info (authenticated)

#### Votes
- `GET /votes/me` - Get current user's votes (authenticated)

## Admin Access

There are two ways to get admin access:

1. **First User**: The very first user to sign up automatically becomes an admin
2. **Admin Email**: Set `ADMIN_EMAIL` in backend `.env` - any user with that email becomes admin

## Firestore Database Structure

### Collections

**users**
```json
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "is_admin": false,
  "created_at": "timestamp"
}
```

**feature_requests**
```json
{
  "title": "Feature title",
  "description": "Feature description",
  "author_id": "user_uid",
  "author_email": "user@example.com",
  "votes": 0,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**votes**
```json
{
  "user_id": "user_uid",
  "request_id": "feature_request_id",
  "created_at": "timestamp"
}
```

## Deployment

### Backend (Google Cloud Run)

```bash
cd backend

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/feedback-board-api

# Deploy to Cloud Run
gcloud run deploy feedback-board-api \
  --image gcr.io/YOUR_PROJECT_ID/feedback-board-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=your_project_id \
  --set-env-vars CORS_ORIGINS=https://your-frontend-domain.com
```

### Frontend (Vercel)

1. Push your code to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Set environment variables in Vercel dashboard
4. Deploy

Or use Vercel CLI:
```bash
cd frontend
npm install -g vercel
vercel --prod
```

## Security Considerations

- All authentication is handled by Firebase
- Backend validates Firebase tokens on every protected request
- Admin privileges are stored in Firestore (not in Firebase Auth custom claims)
- CORS is configured to only allow specified origins
- Environment variables keep sensitive data secure

## Development Tips

### Hot Reload
- Frontend: Automatic with Next.js dev server
- Backend: Use `--reload` flag with uvicorn

### Debugging
- Frontend: Use browser DevTools and React DevTools
- Backend: FastAPI includes interactive API docs at `/docs`

### Adding New Features

1. **Add Database Model**: Update Firestore collections
2. **Create Service**: Add business logic in `backend/app/services/`
3. **Create API Endpoint**: Add route in `backend/app/api/`
4. **Add TypeScript Types**: Update `frontend/src/types/`
5. **Create Component**: Build UI in `frontend/src/components/`

## Troubleshooting

### Firebase Authentication Errors
- Verify Firebase config in `.env.local`
- Check that Email/Password auth is enabled in Firebase Console
- Ensure service account JSON is in the correct location

### CORS Errors
- Check `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL matches exactly (including protocol)

### Firestore Permission Denied
- Verify Firestore is enabled in Firebase Console
- Check that service account has proper permissions
- Ensure `FIREBASE_PROJECT_ID` is correct

## Future Enhancements

- [ ] Comment system on feature requests
- [ ] Status tracking (planned, in progress, completed, rejected)
- [ ] Email notifications
- [ ] Search and filtering
- [ ] Payment processing (Stripe integration)
- [ ] User profiles and avatars
- [ ] Export feature requests to CSV
- [ ] Analytics dashboard for admins

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

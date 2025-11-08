# Lattice Setup Guide

Quick setup guide to run Lattice frontend and backend locally.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd code-2

# Run setup script
chmod +x setup.sh
./setup.sh

# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend (new terminal)
cd frontend && pnpm dev
```

---

## 📋 Prerequisites

- **Node.js** (v18+) - [Download](https://nodejs.org/)
- **pnpm** - Install with: `npm install -g pnpm`
- **Python** (v3.9+) - [Download](https://www.python.org/)
- **pip** (Python package manager)

### Verify installations:

```bash
node --version    # Should be v18+
pnpm --version
python3 --version # Should be 3.9+
pip3 --version
```

---

## 🔧 Backend Setup

```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
APP_NAME="Lattice Backend API"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="your-secret-key-here"
DATABASE_URL="sqlite:///./lattice.db"

# Knot API
KNOT_API_KEY="your-knot-api-key"
KNOT_CLIENT_ID="dda0778d-9486-47f8-bd80-6f2512f9bcdb"
KNOT_ENVIRONMENT="development"
FEATURE_KNOT=true
EOL

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at:** `http://localhost:8000`

### Using ngrok (Optional)

If you need to expose your backend:

```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com

# Expose backend
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok-free.app`) for frontend config.

---

## 🎨 Frontend Setup

```bash
cd frontend

# Install dependencies with pnpm
pnpm install

# Create .env.local
cat > .env.local << EOL
# For local backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# For ngrok backend (if using)
# NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok-free.app

NODE_ENV=development
EOL

# Run frontend
pnpm dev
```

**Frontend runs at:** `http://localhost:3000`

---

## 🎯 Running Both Services

### Terminal 1 - Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend

```bash
cd frontend
pnpm dev
```

---

## 🔑 Knot API Setup

1. Get your Knot credentials from [knotapi.com](https://knotapi.com/)
2. Add to `backend/.env`:
   - `KNOT_API_KEY=your-key-here`
   - `KNOT_CLIENT_ID=your-client-id`

---

## 🌐 Environment Variables

### Backend (.env)

```bash
KNOT_API_KEY=your-knot-api-key        # Required
KNOT_CLIENT_ID=your-client-id         # Required
SECRET_KEY=any-random-string          # Required
DATABASE_URL=sqlite:///./lattice.db   # Required
```

### Frontend (.env.local)

```bash
# Local backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# OR ngrok backend
# NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok-free.app
```

---

## 📱 Using the App

1. Go to `http://localhost:3000/login`
2. Sign up or log in
3. Select a merchant (Amazon, Walmart, Target, etc.)
4. Click "Connect with Knot"
5. Authenticate and get redirected to chat

---

## 🐛 Troubleshooting

### Kill ports if already in use

```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

### Backend issues

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend issues

```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml .next
pnpm install
pnpm dev
```

### Knot SDK not loading

- Check internet connection (SDK loads from CDN)
- Hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)

### Backend logs

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

---

## ✅ Verification

Check if everything is working:

```bash
# Backend health check
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

Open browser to:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

---

## 🔄 Common Commands

### Backend

```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Stop backend
Ctrl + C
```

### Frontend

```bash
# Start frontend
cd frontend && pnpm dev

# Build frontend
pnpm build

# Lint frontend
pnpm lint

# Stop frontend
Ctrl + C
```

---

## 📁 Project Structure

```
code-2/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── integrations/ # Knot integration
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── onboarding/   # Merchant selection
│   │   └── chat/
│   ├── package.json
│   └── .env.local
│
└── SETUP.md
```

---

## 🆘 Quick Help

### Browser console shows success logs

After onboarding, you should see:

```
🎯🎯🎯 onSuccess callback FIRED!
✅✅✅ completeOnboarding SUCCESS!
✅✅✅ SUCCESS: Knot integration working!
```

### Backend terminal shows

```
✅ Knot returned X accounts
✅ Onboarding complete for user X: X accounts linked
```

If you see errors, check:

1. Knot credentials in `backend/.env`
2. Backend is running on port 8000
3. Frontend `.env.local` has correct API URL

---

## 🎉 Success!

If working correctly:

- ✅ Login page loads at `http://localhost:3000/login`
- ✅ Backend responds at `http://localhost:8000/health`
- ✅ Can sign up and connect merchant accounts
- ✅ Console shows successful Knot integration logs

Happy coding! 🚀

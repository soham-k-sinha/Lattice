# Lattice Setup Guide

Complete guide to set up and run Lattice (Frontend + Backend) from GitHub.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd code-2

# Run setup script (creates .env files, installs dependencies)
chmod +x setup.sh
./setup.sh

# Start both services
npm run dev:all
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.9 or higher) - [Download](https://www.python.org/)
- **pip** (Python package manager)
- **Git** - [Download](https://git-scm.com/)

### Verify installations:

```bash
node --version    # Should be v18+
python3 --version # Should be 3.9+
pip3 --version
git --version
```

---

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd code-2
```

### 2. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
# Application Settings
APP_NAME="Lattice Backend API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true

# Security
SECRET_KEY="your-super-secret-key-change-this-in-production"

# Database (SQLite for now)
DATABASE_URL="sqlite:///./lattice.db"

# CORS Origins
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Knot API Integration
KNOT_API_KEY="your-knot-api-key-here"
KNOT_CLIENT_ID="dda0778d-9486-47f8-bd80-6f2512f9bcdb"
KNOT_ENVIRONMENT="development"
FEATURE_KNOT=true

# Logging
LOG_LEVEL="INFO"
EOL

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

---

### 3. Frontend Setup (Next.js)

Open a **new terminal window** and run:

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOL
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
EOL

# Run frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## 🌐 Environment Variables

### Backend (.env)

| Variable | Description | Default/Example |
|----------|-------------|-----------------|
| `APP_NAME` | Application name | "Lattice Backend API" |
| `ENVIRONMENT` | Environment (development/production) | "development" |
| `SECRET_KEY` | JWT secret key | Generate a secure random string |
| `DATABASE_URL` | Database connection string | "sqlite:///./lattice.db" |
| `KNOT_API_KEY` | Your Knot API key | Get from Knot dashboard |
| `KNOT_CLIENT_ID` | Your Knot Client ID | Get from Knot dashboard |
| `KNOT_ENVIRONMENT` | Knot environment (development/production) | "development" |
| `FEATURE_KNOT` | Enable Knot integration | true |

### Frontend (.env.local)

| Variable | Description | Default/Example |
|----------|-------------|-----------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000 |
| `NODE_ENV` | Environment | development |

---

## 🔑 Getting Knot API Credentials

1. Sign up at [Knot API](https://knotapi.com/)
2. Go to your dashboard
3. Create a new application
4. Copy your **API Key** and **Client ID**
5. Add them to your backend `.env` file

---

## 🚀 Running the Application

### Option 1: Run Both Services Separately

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Mac/Linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Run Both Services Together (Recommended)

From the project root:

```bash
# Make sure backend virtual environment is activated first
cd backend && source venv/bin/activate && cd ..

# Run both services
npm run dev:all
```

---

## 📱 Using the Application

### 1. **Sign Up / Login**

Navigate to: http://localhost:3000/login

- Create a new account or login
- You'll be redirected to the onboarding page

### 2. **Connect Merchant Account**

- Select a merchant (Amazon, Walmart, Target, etc.)
- Click "Connect with Knot"
- Complete the merchant authentication
- You'll be redirected to the chat interface

### 3. **Start Chatting**

- Ask questions about your transactions
- Get insights and predictions
- Manage your linked accounts

---

## 🧪 Testing Knot Integration

### Check if Knot SDK is loaded:

Open browser console on http://localhost:3000/onboarding and run:

```javascript
window.KnotapiJS
```

Should return the Knot SDK object.

### Verify Backend Connection:

```bash
# Check backend health
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/
```

### Test Onboarding Flow:

1. Complete merchant selection
2. Watch browser console for logs:
   - `🎯🎯🎯 onSuccess callback FIRED!`
   - `✅✅✅ completeOnboarding SUCCESS!`
   - `✅✅✅ SUCCESS: Knot integration working!`

3. Check backend terminal for:
   - `Fetching accounts for user X from Knot API...`
   - `✅ Knot returned X accounts`

---

## 📁 Project Structure

```
code-2/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── config/        # Configuration
│   │   ├── integrations/  # Knot integration
│   │   ├── middleware/    # Auth middleware
│   │   ├── models/        # Data models
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── login/         # Login page
│   │   ├── onboarding/    # Merchant connection
│   │   ├── chat/          # Chat interface
│   │   └── layout.tsx     # Root layout
│   ├── components/        # React components
│   ├── lib/              # API client
│   ├── package.json
│   └── .env.local
│
└── SETUP.md              # This file
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

**Module not found errors:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Database errors:**
```bash
# Delete and recreate database
rm backend/lattice.db
# Backend will auto-create on next run
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9
```

**Module not found errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Knot SDK not loading:**
- Check browser console for errors
- Verify internet connection (SDK loads from CDN)
- Try hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)

### Hydration Errors (Grammarly Extension)

If you see hydration mismatch warnings:
1. These are caused by browser extensions (Grammarly, etc.)
2. They're harmless - the app will still work
3. To remove them: Disable browser extensions temporarily

### Knot 429 Rate Limit Errors

If you see `429 Bad Request` errors:
1. Wait 2-3 minutes between onboarding attempts
2. Don't repeatedly test the same merchant connection
3. Use development mode (automatically enabled)

### Backend Can't Connect to Knot API

1. Verify your `KNOT_API_KEY` in backend `.env`
2. Check `KNOT_ENVIRONMENT` is set to "development"
3. Ensure `FEATURE_KNOT=true`
4. Check backend logs for detailed error messages

---

## 🔒 Security Notes

### For Development:
- Use the default SQLite database
- Keep `DEBUG=true` for detailed error messages
- Use `KNOT_ENVIRONMENT="development"` for testing

### For Production:
- Change `SECRET_KEY` to a secure random string
- Set `DEBUG=false`
- Use PostgreSQL instead of SQLite
- Update `CORS_ORIGINS` to your production domain
- Use `KNOT_ENVIRONMENT="production"`
- Enable HTTPS

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🆘 Getting Help

### Check Logs

**Backend logs:**
- Look at the terminal running `uvicorn`
- Check for errors with `❌` prefix

**Frontend logs:**
- Open browser DevTools (F12)
- Go to Console tab
- Look for errors (red messages)

### Common Commands

```bash
# Check if services are running
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Restart services
# Backend: Ctrl+C then re-run uvicorn
# Frontend: Ctrl+C then re-run npm run dev

# View backend logs with more detail
cd backend
source venv/bin/activate
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Clear frontend cache
cd frontend
rm -rf .next
npm run dev
```

---

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Node.js v18+ installed
- [ ] Python 3.9+ installed
- [ ] Backend `.env` file exists with all variables
- [ ] Frontend `.env.local` file exists
- [ ] Backend running on port 8000 (`curl http://localhost:8000/health`)
- [ ] Frontend running on port 3000 (browser opens)
- [ ] Knot API credentials are valid
- [ ] No other services using ports 3000 or 8000

---

## 🎉 Success!

If everything is working:
1. You should see the login page at http://localhost:3000/login
2. Backend should respond at http://localhost:8000/health
3. You can sign up, onboard, and connect merchant accounts
4. Browser console shows successful Knot integration logs

Happy coding! 🚀


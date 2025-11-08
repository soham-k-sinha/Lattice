# Lattice - Think with your money

An AI co-pilot that plans, predicts, and pays.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd code-2
chmod +x setup.sh
./setup.sh
```

Then start both services:

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && pnpm dev
```

Open `http://localhost:3000` 🎉

## 📖 Documentation

See [SETUP.md](./SETUP.md) for detailed setup, troubleshooting, and configuration.

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, pnpm
- **Backend**: FastAPI, Python, SQLite
- **Integration**: Knot API

## ✨ Features

- 🔐 Secure authentication
- 🏪 Multi-merchant linking (Amazon, Walmart, Target, etc.)
- 💬 AI financial chat interface
- 📊 Transaction tracking
- 🔄 Real-time sync

## 📋 Prerequisites

- Node.js v18+
- pnpm (`npm install -g pnpm`)
- Python 3.9+
- Knot API credentials

## 🌐 URLs

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🔑 Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add KNOT_API_KEY to .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
# Configure NEXT_PUBLIC_API_URL in .env.local
pnpm dev
```

## 🐛 Quick Fixes

```bash
# Kill hung processes
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Reinstall frontend
cd frontend && rm -rf node_modules .next pnpm-lock.yaml && pnpm install

# Reinstall backend
cd backend && source venv/bin/activate && pip install -r requirements.txt
```

## 📝 Environment Variables

### backend/.env
```bash
KNOT_API_KEY=your-key
KNOT_CLIENT_ID=your-client-id
SECRET_KEY=any-secret
```

### frontend/.env.local
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🆘 Support

See [SETUP.md](./SETUP.md) for troubleshooting and detailed instructions.

---

Built with ❤️ by the Lattice team

# Lattice - Think with your money

An AI co-pilot that plans, predicts, and pays. Lattice helps you understand your financial transactions and make smarter decisions.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd code-2

# Run automated setup
chmod +x setup.sh
./setup.sh

# Follow the on-screen instructions to start the app
```

## 📖 Full Documentation

See [SETUP.md](./SETUP.md) for detailed setup instructions, troubleshooting, and API documentation.

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Framer Motion
- **Backend**: FastAPI (Python) with JWT authentication
- **Integration**: Knot API for merchant account linking and transaction sync

## ✨ Features

- 🔐 Secure authentication and authorization
- 🏪 Multi-merchant account linking (Amazon, Walmart, Target, etc.)
- 💬 AI-powered chat interface for financial insights
- 📊 Transaction tracking and analysis
- 🔄 Real-time sync with merchant accounts
- 📱 Modern, responsive UI

## 🛠️ Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion
- Knot SDK

### Backend
- FastAPI
- Python 3.9+
- SQLite (development) / PostgreSQL (production)
- JWT Authentication
- Knot API Integration

## 📋 Prerequisites

- Node.js v18 or higher
- Python 3.9 or higher
- pip (Python package manager)
- Knot API credentials

## 🔧 Manual Setup

If you prefer manual setup over the automated script:

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env file (see SETUP.md)
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
# Create .env.local file (see SETUP.md)
npm run dev
```

See [SETUP.md](./SETUP.md) for detailed instructions.

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📱 Usage

1. Navigate to http://localhost:3000/login
2. Sign up or log in
3. Select a merchant to connect
4. Authenticate with your merchant account
5. Start chatting with your AI financial assistant

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

## 🐛 Troubleshooting

See the [Troubleshooting section in SETUP.md](./SETUP.md#-troubleshooting) for common issues and solutions.

## 📝 Environment Variables

### Backend (.env)
- `KNOT_API_KEY` - Your Knot API key (required)
- `KNOT_CLIENT_ID` - Your Knot Client ID (required)
- `SECRET_KEY` - JWT secret key
- `DATABASE_URL` - Database connection string

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL

See [SETUP.md](./SETUP.md#-environment-variables) for complete list.

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel
```

### Backend (Render/Railway/etc.)
- Set environment variables
- Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Connect your Git repository

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For detailed setup instructions, troubleshooting, and API documentation, see [SETUP.md](./SETUP.md).

---

Built with ❤️ by the Lattice team


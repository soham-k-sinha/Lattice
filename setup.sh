#!/bin/bash

# Lattice Setup Script
# Sets up backend (Python) and frontend (Node.js with pnpm)

set -e

echo "🚀 Starting Lattice Setup..."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not installed. Install from https://nodejs.org/${NC}"
    exit 1
fi
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js v18+ required. Current: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node -v)${NC}"

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}⚠️  pnpm not installed. Installing...${NC}"
    npm install -g pnpm
    echo -e "${GREEN}✅ pnpm installed${NC}"
else
    echo -e "${GREEN}✅ pnpm $(pnpm -v)${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not installed. Install from https://www.python.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 installed${NC}"

echo ""
echo "🔧 Setting up Backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment exists${NC}"
fi

# Activate and install
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Create .env
if [ ! -f ".env" ]; then
    echo "Creating backend .env..."
    cat > .env << 'EOL'
APP_NAME="Lattice Backend API"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="dev-secret-key-change-me"
DATABASE_URL="sqlite:///./lattice.db"

# Knot API
KNOT_API_KEY="your-knot-api-key-here"
KNOT_CLIENT_ID="dda0778d-9486-47f8-bd80-6f2512f9bcdb"
KNOT_ENVIRONMENT="development"
FEATURE_KNOT=true
EOL
    echo -e "${GREEN}✅ Backend .env created${NC}"
    echo -e "${YELLOW}⚠️  Add your KNOT_API_KEY in backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env exists, skipping${NC}"
fi

cd ..

echo ""
echo "🎨 Setting up Frontend..."

cd frontend

echo "Installing dependencies with pnpm..."
pnpm install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Create .env.local
if [ ! -f ".env.local" ]; then
    echo "Creating frontend .env.local..."
    cat > .env.local << 'EOL'
# Local backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# If using ngrok, uncomment and update:
# NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok-free.app

NODE_ENV=development
EOL
    echo -e "${GREEN}✅ Frontend .env.local created${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend .env.local exists, skipping${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅✅✅ Setup Complete! ✅✅✅${NC}"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Add Knot API credentials to ${BLUE}backend/.env${NC}"
echo ""
echo "2. Start backend (Terminal 1):"
echo -e "   ${BLUE}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Start frontend (Terminal 2):"
echo -e "   ${BLUE}cd frontend && pnpm dev${NC}"
echo ""
echo "4. Open browser:"
echo -e "   ${BLUE}http://localhost:3000${NC}"
echo ""
echo "🎉 Happy coding!"

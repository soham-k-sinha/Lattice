#!/bin/bash

# Lattice Setup Script
# Automatically sets up both frontend and backend

set -e  # Exit on error

echo "🚀 Starting Lattice Setup..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js v18+ from https://nodejs.org/${NC}"
    exit 1
fi
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js v18+ required. Current version: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node -v) installed${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9+ from https://www.python.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version) installed${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed. Please install pip3${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 installed${NC}"

echo ""
echo "🔧 Setting up Backend..."

# Backend setup
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cat > .env << 'EOL'
# Application Settings
APP_NAME="Lattice Backend API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true

# Security
SECRET_KEY="dev-secret-key-change-in-production-$(openssl rand -hex 32)"

# Database (SQLite for development)
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
    echo -e "${GREEN}✅ Backend .env file created${NC}"
    echo -e "${YELLOW}⚠️  Remember to add your KNOT_API_KEY in backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env file already exists, skipping...${NC}"
fi

cd ..

echo ""
echo "🎨 Setting up Frontend..."

# Frontend setup
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install
echo -e "${GREEN}✅ Node.js dependencies installed${NC}"

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating frontend .env.local file..."
    cat > .env.local << 'EOL'
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
EOL
    echo -e "${GREEN}✅ Frontend .env.local file created${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend .env.local file already exists, skipping...${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅✅✅ Setup Complete! ✅✅✅${NC}"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Add your Knot API credentials to backend/.env:"
echo "   - KNOT_API_KEY=your-api-key"
echo ""
echo "2. Start the backend (in one terminal):"
echo -e "   ${BLUE}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Start the frontend (in another terminal):"
echo -e "   ${BLUE}cd frontend && npm run dev${NC}"
echo ""
echo "4. Open your browser and go to:"
echo -e "   ${BLUE}http://localhost:3000${NC}"
echo ""
echo "For more information, see SETUP.md"
echo ""
echo "🎉 Happy coding!"


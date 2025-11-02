#!/bin/bash

# Ikodio ERP - Development Environment Setup Script

set -e

echo "==================================="
echo "Ikodio ERP - Development Setup"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}ERROR: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Setting up Backend...${NC}"
cd backend

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements/development.txt

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please update .env file with your database credentials${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

cd ..

echo -e "${YELLOW}Step 2: Setting up Frontend...${NC}"
cd frontend

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "Node.js version: $NODE_VERSION"

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

cd ..

echo "==================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Setup database connection: ./scripts/setup-database.sh"
echo "2. Update backend/.env with your database credentials"
echo "3. Run migrations: cd backend && python manage.py migrate"
echo "4. Create superuser: cd backend && python manage.py createsuperuser"
echo "5. Start backend: cd backend && python manage.py runserver"
echo "6. Start frontend: cd frontend && npm run dev"
echo ""
echo "Happy coding! 🚀"

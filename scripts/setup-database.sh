#!/bin/bash

# Ikodio ERP - Database Setup Script
# This script sets up SSH tunnel to remote PostgreSQL server and creates database

set -e

echo "==================================="
echo "Ikodio ERP - Database Setup"
echo "==================================="
echo ""

# Configuration
SSH_USER="ikodioxlapo"
SSH_HOST="192.168.0.100"
SSH_PORT="7420"
DB_NAME="ikodio_erp"
DB_USER="ikodioxlapo"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Testing SSH connection...${NC}"
ssh -p $SSH_PORT -o ConnectTimeout=10 $SSH_USER@$SSH_HOST "echo 'SSH connection successful!'" || {
    echo -e "${RED}ERROR: Cannot connect to SSH server${NC}"
    echo "Please check:"
    echo "1. SSH server is running on $SSH_HOST:$SSH_PORT"
    echo "2. You have correct SSH credentials"
    echo "3. Firewall allows connection"
    exit 1
}

echo -e "${GREEN}✓ SSH connection successful${NC}"
echo ""

echo -e "${YELLOW}Step 2: Setting up SSH tunnel for PostgreSQL...${NC}"
echo "This will create a tunnel: localhost:5432 -> $SSH_HOST:5432"
echo "You can stop the tunnel with Ctrl+C"
echo ""

# Check if port 5432 is already in use
if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}Warning: Port 5432 is already in use${NC}"
    echo "Attempting to use port 5433 instead..."
    LOCAL_PORT=5433
else
    LOCAL_PORT=5432
fi

echo -e "${GREEN}Starting SSH tunnel...${NC}"
echo "Local port: $LOCAL_PORT"
echo "Remote: $SSH_HOST:5432"
echo ""

# Create SSH tunnel
ssh -p $SSH_PORT -L $LOCAL_PORT:localhost:5432 -N $SSH_USER@$SSH_HOST &
SSH_PID=$!

# Wait a moment for tunnel to establish
sleep 2

# Check if tunnel is running
if ps -p $SSH_PID > /dev/null; then
    echo -e "${GREEN}✓ SSH tunnel established (PID: $SSH_PID)${NC}"
    echo ""
    
    echo -e "${YELLOW}Step 3: Creating database...${NC}"
    ssh -p $SSH_PORT $SSH_USER@$SSH_HOST "psql -c 'CREATE DATABASE $DB_NAME;' || echo 'Database may already exist'"
    
    echo -e "${GREEN}✓ Database setup complete${NC}"
    echo ""
    echo "==================================="
    echo "Database Configuration:"
    echo "==================================="
    echo "DB_NAME=$DB_NAME"
    echo "DB_USER=$DB_USER"
    echo "DB_HOST=localhost"
    echo "DB_PORT=$LOCAL_PORT"
    echo ""
    echo "Update your backend/.env file with these settings"
    echo ""
    echo -e "${YELLOW}SSH Tunnel is running...${NC}"
    echo "Press Ctrl+C to stop the tunnel"
    echo ""
    
    # Wait for user to stop
    wait $SSH_PID
else
    echo -e "${RED}ERROR: Failed to establish SSH tunnel${NC}"
    exit 1
fi

#!/bin/bash
# Deployment script for Ikodio ERP

set -e

echo "🚀 Deploying Ikodio ERP to Server..."

SERVER_USER="ikodioxlapo"
SERVER_HOST="192.168.0.100"
SERVER_PORT="7420"
DEPLOY_PATH="/home/ikodioxlapo/ikodio-erp"

echo "📦 Creating deployment package..."

# Create temp directory for deployment
TEMP_DIR=$(mktemp -d)
echo "Temporary directory: $TEMP_DIR"

# Copy backend
echo "Copying backend..."
cp -r backend $TEMP_DIR/
rm -rf $TEMP_DIR/backend/venv
rm -rf $TEMP_DIR/backend/__pycache__
rm -rf $TEMP_DIR/backend/*/__pycache__
rm -rf $TEMP_DIR/backend/staticfiles
rm -rf $TEMP_DIR/backend/media
rm -rf $TEMP_DIR/backend/logs

# Copy frontend
echo "Copying frontend..."
cp -r frontend $TEMP_DIR/
rm -rf $TEMP_DIR/frontend/node_modules
rm -rf $TEMP_DIR/frontend/dist

# Create archive
echo "Creating archive..."
cd $TEMP_DIR
tar -czf ikodio-erp.tar.gz backend frontend

echo "📤 Transferring to server..."
scp -P $SERVER_PORT ikodio-erp.tar.gz $SERVER_USER@$SERVER_HOST:~/

echo "🔧 Setting up on server..."
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
    # Extract files
    mkdir -p ~/ikodio-erp
    cd ~/ikodio-erp
    tar -xzf ~/ikodio-erp.tar.gz
    rm ~/ikodio-erp.tar.gz
    
    # Setup backend
    cd ~/ikodio-erp/backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements/production.txt
    
    # Create necessary directories
    mkdir -p logs staticfiles media
    
    echo "✅ Backend setup complete!"
    
    # Setup frontend
    cd ~/ikodio-erp/frontend
    npm install
    npm run build
    
    echo "✅ Frontend setup complete!"
ENDSSH

# Cleanup
rm -rf $TEMP_DIR

echo "✅ Deployment complete!"
echo "Next steps:"
echo "1. Configure Nginx"
echo "2. Setup Gunicorn service"
echo "3. Run migrations"
echo "4. Collect static files"

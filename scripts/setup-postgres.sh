#!/bin/bash
# Script to setup PostgreSQL database for iKodio ERP

echo "🔧 Setting up PostgreSQL database for iKodio ERP..."

# Database credentials
DB_NAME="erp_ikodio_db"
DB_USER="erp_admin"
DB_PASSWORD="Mi2525252512"

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running!"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Try to connect and create database and user
psql postgres << EOF
-- Drop existing if any
DROP DATABASE IF EXISTS ${DB_NAME};
DROP USER IF EXISTS ${DB_USER};

-- Create user
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- Create database
CREATE DATABASE ${DB_NAME}
    WITH 
    OWNER = ${DB_USER}
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER USER ${DB_USER} CREATEDB;

-- Display results
\l ${DB_NAME}
\du ${DB_USER}
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database and user created successfully!"
    echo ""
    echo "📝 Connection details:"
    echo "   Database: ${DB_NAME}"
    echo "   User: ${DB_USER}"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo ""
    echo "🧪 Testing connection..."
    PGPASSWORD="${DB_PASSWORD}" psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "SELECT current_database(), current_user, version();"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Connection test successful!"
    else
        echo ""
        echo "❌ Connection test failed!"
    fi
else
    echo "❌ Failed to create database and user!"
    echo "Please make sure you can connect to PostgreSQL as superuser"
fi

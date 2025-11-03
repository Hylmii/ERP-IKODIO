#!/bin/bash
echo "🔧 Setting up PostgreSQL database for iKodio ERP..."
echo ""
echo "Silakan masukkan kredensial PostgreSQL superuser Anda:"
read -p "PostgreSQL superuser (default: postgres): " PG_SUPERUSER
PG_SUPERUSER=${PG_SUPERUSER:-postgres}

echo ""
echo "📋 Akan membuat:"
echo "   Database: erp_ikodio_db"
echo "   User: erp_admin"
echo "   Password: Mi2525252512"
echo ""

psql -U $PG_SUPERUSER -d postgres << 'SQL'
-- Drop existing if any
DROP DATABASE IF EXISTS erp_ikodio_db;
DROP USER IF EXISTS erp_admin;

-- Create user
CREATE USER erp_admin WITH PASSWORD 'Mi2525252512';

-- Create database
CREATE DATABASE erp_ikodio_db
    WITH 
    OWNER = erp_admin
    ENCODING = 'UTF8'
    TEMPLATE = template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE erp_ikodio_db TO erp_admin;
ALTER USER erp_admin CREATEDB;

-- Connect and grant schema privileges
\c erp_ikodio_db
GRANT ALL ON SCHEMA public TO erp_admin;

-- Display results
\l erp_ikodio_db
\du erp_admin
SQL

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database created successfully!"
    echo ""
    echo "🧪 Testing connection..."
    PGPASSWORD='Mi2525252512' psql -h localhost -U erp_admin -d erp_ikodio_db -c "SELECT current_database(), current_user;"
fi

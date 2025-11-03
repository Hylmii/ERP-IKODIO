-- Create database and user for iKodio ERP
-- Run this as PostgreSQL superuser

-- Create user
CREATE USER erp_admin WITH PASSWORD 'Mi2525252512';

-- Create database
CREATE DATABASE erp_ikodio_db
    WITH 
    OWNER = erp_admin
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE erp_ikodio_db TO erp_admin;

-- Connect to the new database and grant schema privileges
\c erp_ikodio_db
GRANT ALL ON SCHEMA public TO erp_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO erp_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO erp_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO erp_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO erp_admin;

-- Display confirmation
\l erp_ikodio_db
\du erp_admin

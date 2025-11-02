# Production Deployment Guide

## Table of Contents

1. [Server Requirements](#server-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Setup](#server-setup)
4. [Database Setup](#database-setup)
5. [Application Deployment](#application-deployment)
6. [Nginx Configuration](#nginx-configuration)
7. [SSL/HTTPS Setup](#sslhttps-setup)
8. [Environment Variables](#environment-variables)
9. [Database Backup & Recovery](#database-backup--recovery)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Server Requirements

### Minimum Specifications

| Component | Requirement |
|-----------|-------------|
| **OS** | Ubuntu 22.04 LTS (recommended) |
| **CPU** | 4 cores (8 cores recommended) |
| **RAM** | 8 GB (16 GB recommended) |
| **Storage** | 100 GB SSD |
| **Network** | 1 Gbps |

### Recommended Specifications (Production)

| Component | Specification |
|-----------|---------------|
| **OS** | Ubuntu 22.04 LTS |
| **CPU** | 8 cores (Intel Xeon or AMD EPYC) |
| **RAM** | 32 GB |
| **Storage** | 500 GB NVMe SSD |
| **Network** | 10 Gbps |
| **Backup** | Separate backup storage (1 TB+) |

---

## Pre-Deployment Checklist

### Domain & DNS

- [ ] Domain purchased and configured
- [ ] DNS A record pointing to server IP
- [ ] DNS AAAA record for IPv6 (optional)
- [ ] DNS propagation completed (24-48 hours)

### SSL Certificate

- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Certificate auto-renewal configured
- [ ] Certificate chain verified

### Credentials & Access

- [ ] Server SSH access configured
- [ ] Database credentials generated
- [ ] Redis password set
- [ ] Django SECRET_KEY generated
- [ ] Email credentials (SMTP)
- [ ] Cloud storage credentials (AWS S3, etc.)

### Code Repository

- [ ] All changes committed
- [ ] Code pushed to production branch
- [ ] Database migrations tested
- [ ] Static files collected
- [ ] Environment variables documented

---

## Server Setup

### 1. Initial Server Configuration

```bash
# Connect to server
ssh root@your-server-ip

# Update system packages
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone Asia/Jakarta

# Set hostname
hostnamectl set-hostname erp.ikodio.com

# Create deploy user
adduser deploy
usermod -aG sudo deploy

# Setup SSH for deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Disable root SSH login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Setup UFW firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
```

### 2. Install Docker & Docker Compose

```bash
# Login as deploy user
su - deploy

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Logout and login again for group changes to take effect
exit
su - deploy

# Verify Docker installation
docker --version

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify Docker Compose installation
docker-compose --version
```

### 3. Install Nginx

```bash
# Install Nginx
sudo apt install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify Nginx is running
sudo systemctl status nginx
```

### 4. Install Certbot for SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Verify Certbot installation
certbot --version
```

---

## Database Setup

### Option 1: PostgreSQL on Same Server

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ikodio_erp_production;
CREATE USER ikodio_user WITH PASSWORD 'your_strong_password_here';
ALTER ROLE ikodio_user SET client_encoding TO 'utf8';
ALTER ROLE ikodio_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ikodio_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ikodio_erp_production TO ikodio_user;
\q
EOF

# Allow local connections
sudo sed -i '/^host/s/ident/md5/' /etc/postgresql/*/main/pg_hba.conf
sudo sed -i '/^local/s/peer/trust/' /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql
```

### Option 2: Managed PostgreSQL (Recommended)

**Using AWS RDS, Azure Database, or DigitalOcean Managed Database:**

1. Create PostgreSQL 15+ instance
2. Note connection details:
   - Host: `your-db-host.region.cloud.com`
   - Port: `5432`
   - Database: `ikodio_erp_production`
   - Username: `ikodio_user`
   - Password: `your_strong_password`

3. Configure firewall to allow server IP
4. Enable SSL connections
5. Setup automated backups

### Redis Setup

```bash
# Install Redis
sudo apt install redis-server -y

# Configure Redis
sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
sudo sed -i 's/# requirepass foobared/requirepass your_redis_password/' /etc/redis/redis.conf

# Restart Redis
sudo systemctl restart redis
sudo systemctl enable redis

# Test Redis
redis-cli
AUTH your_redis_password
PING  # Should return PONG
exit
```

---

## Application Deployment

### 1. Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www/ikodio-erp-production
sudo chown deploy:deploy /var/www/ikodio-erp-production

# Clone repository
cd /var/www
git clone https://github.com/your-username/ikodio-erp.git ikodio-erp-production
cd ikodio-erp-production

# Checkout production branch
git checkout main
```

### 2. Create Production Environment File

```bash
# Create .env file
nano .env
```

Add the following (see [Environment Variables](#environment-variables) section for complete list):

```env
# Django
DEBUG=False
SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=erp.ikodio.com,www.erp.ikodio.com

# Database
DATABASE_URL=postgresql://ikodio_user:password@localhost:5432/ikodio_erp_production

# Redis
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. Create Production Docker Compose File

```bash
nano docker-compose.prod.yml
```

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ikodio_backend_prod
    restart: always
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - redis
    networks:
      - ikodio_network
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ikodio_celery_worker_prod
    restart: always
    env_file:
      - .env
    depends_on:
      - redis
      - backend
    networks:
      - ikodio_network
    command: celery -A config worker -l info --concurrency=4

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ikodio_celery_beat_prod
    restart: always
    env_file:
      - .env
    depends_on:
      - redis
      - backend
    networks:
      - ikodio_network
    command: celery -A config beat -l info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=https://erp.ikodio.com/api
    container_name: ikodio_frontend_prod
    restart: always
    ports:
      - "3000:80"
    networks:
      - ikodio_network

  redis:
    image: redis:7-alpine
    container_name: ikodio_redis_prod
    restart: always
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis_data:/data
    networks:
      - ikodio_network

volumes:
  static_volume:
  media_volume:
  redis_data:

networks:
  ikodio_network:
    driver: bridge
```

### 4. Build and Start Containers

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start containers
docker-compose -f docker-compose.prod.yml up -d

# Verify containers are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Run Migrations and Collect Static Files

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Load initial data (optional)
docker-compose -f docker-compose.prod.yml exec backend python manage.py seed_data
```

---

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/ikodio-erp
```

```nginx
# Upstream for Django backend
upstream backend {
    server localhost:8000;
}

# Upstream for React frontend
upstream frontend {
    server localhost:3000;
}

# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name erp.ikodio.com www.erp.ikodio.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name erp.ikodio.com www.erp.ikodio.com;
    
    # SSL certificates (will be configured by Certbot)
    ssl_certificate /etc/letsencrypt/live/erp.ikodio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.ikodio.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/erp.ikodio.com/chain.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Max upload size
    client_max_body_size 50M;
    
    # Logging
    access_log /var/log/nginx/ikodio-erp-access.log;
    error_log /var/log/nginx/ikodio-erp-error.log;
    
    # API backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/ikodio-erp-production/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/ikodio-erp-production/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. Enable Site and Test Configuration

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/ikodio-erp /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## SSL/HTTPS Setup

### 1. Obtain SSL Certificate with Let's Encrypt

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d erp.ikodio.com -d www.erp.ikodio.com

# Start Nginx
sudo systemctl start nginx

# Test automatic renewal
sudo certbot renew --dry-run
```

### 2. Setup Auto-Renewal

Certbot automatically creates a systemd timer. Verify it:

```bash
# Check timer status
sudo systemctl status certbot.timer

# List timers
sudo systemctl list-timers | grep certbot
```

---

## Environment Variables

### Complete .env File Template

```env
# ============================================================================
# DJANGO SETTINGS
# ============================================================================
DEBUG=False
SECRET_KEY=your-secret-key-min-50-characters-random-string-here
ALLOWED_HOSTS=erp.ikodio.com,www.erp.ikodio.com
DJANGO_SETTINGS_MODULE=config.settings

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_URL=postgresql://ikodio_user:your_password@your-db-host:5432/ikodio_erp_production
DB_NAME=ikodio_erp_production
DB_USER=ikodio_user
DB_PASSWORD=your_database_password
DB_HOST=your-db-host.region.cloud.com
DB_PORT=5432

# ============================================================================
# REDIS
# ============================================================================
REDIS_URL=redis://:your_redis_password@localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# ============================================================================
# CELERY
# ============================================================================
CELERY_BROKER_URL=redis://:your_redis_password@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:your_redis_password@localhost:6379/2

# ============================================================================
# EMAIL
# ============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=iKodio ERP <noreply@ikodio.com>

# ============================================================================
# SECURITY
# ============================================================================
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# ============================================================================
# CORS
# ============================================================================
CORS_ALLOWED_ORIGINS=https://erp.ikodio.com,https://www.erp.ikodio.com
CORS_ALLOW_CREDENTIALS=True

# ============================================================================
# AWS S3 (Optional - for media storage)
# ============================================================================
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=ikodio-erp-media
AWS_S3_REGION_NAME=ap-southeast-1
AWS_S3_CUSTOM_DOMAIN=${AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# ============================================================================
# FRONTEND
# ============================================================================
VITE_API_URL=https://erp.ikodio.com/api
```

### Generate SECRET_KEY

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Database Backup & Recovery

### 1. Automated Backup Script

Create backup script:

```bash
sudo nano /usr/local/bin/backup-ikodio-db.sh
```

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/ikodio-erp"
DB_NAME="ikodio_erp_production"
DB_USER="ikodio_user"
DB_HOST="localhost"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ikodio_erp_$TIMESTAMP.sql.gz"

# Perform backup
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    
    # Delete old backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # Upload to S3 (optional)
    # aws s3 cp $BACKUP_FILE s3://your-backup-bucket/database/
else
    echo "Backup failed!"
    exit 1
fi
```

Make executable:

```bash
sudo chmod +x /usr/local/bin/backup-ikodio-db.sh
```

### 2. Setup Cron Job

```bash
sudo crontab -e
```

Add daily backup at 2 AM:

```cron
0 2 * * * /usr/local/bin/backup-ikodio-db.sh >> /var/log/ikodio-backup.log 2>&1
```

### 3. Manual Backup

```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Or using pg_dump
PGPASSWORD=your_password pg_dump -h localhost -U ikodio_user ikodio_erp_production | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 4. Recovery

```bash
# Restore from JSON
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py loaddata backup_20241103.json

# Or restore from SQL
gunzip < backup_20241103.sql.gz | PGPASSWORD=your_password psql -h localhost -U ikodio_user ikodio_erp_production
```

---

## Monitoring & Maintenance

### 1. System Monitoring

Install monitoring tools:

```bash
# Install htop
sudo apt install htop -y

# Install netdata (optional)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### 2. Log Monitoring

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100 backend

# View Nginx logs
sudo tail -f /var/log/nginx/ikodio-erp-access.log
sudo tail -f /var/log/nginx/ikodio-erp-error.log

# View system logs
sudo journalctl -u nginx -f
sudo journalctl -u postgresql -f
```

### 3. Performance Monitoring

```bash
# Check Docker resource usage
docker stats

# Check disk usage
df -h

# Check PostgreSQL connections
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell -c "SELECT count(*) FROM pg_stat_activity;"
```

### 4. Regular Maintenance Tasks

```bash
# Update system packages (monthly)
sudo apt update && sudo apt upgrade -y

# Clean Docker
docker system prune -a --volumes -f

# Vacuum PostgreSQL (weekly)
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell -c "VACUUM ANALYZE;"

# Check disk space
df -h

# Rotate logs
sudo logrotate -f /etc/logrotate.conf
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart containers
docker-compose -f docker-compose.prod.yml restart

# Rebuild if necessary
docker-compose -f docker-compose.prod.yml up -d --build
```

### Database Connection Issues

```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python manage.py check --database default

# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection from backend container
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### High CPU/Memory Usage

```bash
# Check resource usage
docker stats

# Identify problematic process
htop

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Scale workers if needed
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=2
```

### SSL Certificate Issues

```bash
# Check certificate expiry
sudo certbot certificates

# Renew manually
sudo certbot renew

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

**Last Updated:** November 3, 2025  
**Version:** 1.0  
**Contact:** devops@ikodio.com

# CI/CD Pipeline Documentation

## Overview

The iKodio ERP project uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). The pipeline automatically tests, builds, and deploys the application to staging and production environments.

## Pipeline Stages

### 1. Backend Testing & Linting

**Triggers:** Push or Pull Request to `main` or `develop` branches

**Services:**
- PostgreSQL 15 (test database)
- Redis 7 (caching)

**Steps:**
1. **Code Checkout** - Get latest code from repository
2. **Python Setup** - Install Python 3.11
3. **Dependencies Installation** - Install packages from `requirements/development.txt`
4. **Flake8 Linting** - Check code quality and style
   - Error checking (E9, F63, F7, F82)
   - Complexity analysis (max complexity: 10)
   - Line length check (max 127 characters)
5. **Black Formatting Check** - Ensure code follows black style
6. **Isort Import Check** - Verify import sorting
7. **Database Migrations** - Apply all migrations to test database
8. **Unit Tests with Coverage** - Run all tests with coverage report
9. **Coverage Upload** - Upload coverage to Codecov

**Environment Variables:**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ikodio_erp_test
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key-for-ci-cd-pipeline
DEBUG=True
```

### 2. Frontend Testing & Linting

**Triggers:** Push or Pull Request to `main` or `develop` branches

**Steps:**
1. **Code Checkout** - Get latest code
2. **Node.js Setup** - Install Node.js 18
3. **Dependencies Installation** - `npm ci` for clean install
4. **ESLint** - JavaScript/TypeScript linting
5. **TypeScript Type Checking** - Compile check without output
6. **Unit Tests** - Run tests with coverage
7. **Production Build** - Verify build succeeds
8. **Coverage Upload** - Upload frontend coverage to Codecov

### 3. Security Scanning

**Triggers:** Push or Pull Request to `main` or `develop` branches

**Steps:**
1. **Safety Check** - Scan Python dependencies for known vulnerabilities
2. **Bandit Scan** - Security issues in Python code
3. **NPM Audit** - Check npm packages for vulnerabilities

**Note:** These steps continue on error to not block the pipeline, but warnings are reported.

### 4. Docker Build

**Triggers:** After successful backend and frontend tests

**Steps:**
1. **Setup Docker Buildx** - Enable advanced Docker features
2. **Build Backend Image** - Create Docker image for Django backend
3. **Build Frontend Image** - Create Docker image for React frontend
4. **Cache Management** - Use GitHub Actions cache for faster builds

**Images Created:**
- `ikodio-erp-backend:${GITHUB_SHA}`
- `ikodio-erp-frontend:${GITHUB_SHA}`

### 5. Deploy to Staging

**Triggers:** 
- Only on `main` branch
- Only on push (not PR)
- After all tests pass

**Environment:** staging (https://staging.ikodio.com)

**Steps:**
1. **SSH to Staging Server**
2. **Pull Latest Code** - `git pull origin main`
3. **Docker Compose Pull** - Get latest images
4. **Docker Compose Up** - Build and start containers
5. **Run Migrations** - Apply database changes
6. **Collect Static Files** - Gather static assets
7. **Slack Notification** - Notify team of deployment status

**Required Secrets:**
- `STAGING_HOST` - Staging server IP/hostname
- `STAGING_USERNAME` - SSH username
- `STAGING_SSH_KEY` - SSH private key
- `STAGING_PORT` - SSH port (default: 22)
- `SLACK_WEBHOOK` - Slack webhook URL for notifications

### 6. Deploy to Production

**Triggers:**
- Only on `main` branch
- Only on push (not PR)
- Requires manual approval
- After all tests pass

**Environment:** production (https://erp.ikodio.com)

**Steps:**
1. **Manual Approval** - Team lead must approve deployment
2. **SSH to Production Server**
3. **Pull Latest Code** - `git pull origin main`
4. **Docker Compose Pull** - Get latest images
5. **Docker Compose Up** - Build and start containers
6. **Run Migrations** - Apply database changes
7. **Collect Static Files** - Gather static assets
8. **Restart Services** - Graceful restart
9. **Smoke Tests** - Verify health endpoint
10. **Slack Notification** - Notify team of deployment status

**Required Secrets:**
- `PRODUCTION_HOST` - Production server IP/hostname
- `PRODUCTION_USERNAME` - SSH username
- `PRODUCTION_SSH_KEY` - SSH private key
- `PRODUCTION_PORT` - SSH port (default: 22)
- `SLACK_WEBHOOK` - Slack webhook URL for notifications

## GitHub Secrets Configuration

### Required Secrets

Navigate to: `Settings > Secrets and variables > Actions > New repository secret`

#### Staging Environment
```
STAGING_HOST=staging.ikodio.com
STAGING_USERNAME=deploy
STAGING_SSH_KEY=<private_key_content>
STAGING_PORT=22
```

#### Production Environment
```
PRODUCTION_HOST=erp.ikodio.com
PRODUCTION_USERNAME=deploy
PRODUCTION_SSH_KEY=<private_key_content>
PRODUCTION_PORT=22
```

#### Notifications
```
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Optional (for Docker Registry)
```
DOCKER_USERNAME=<dockerhub_username>
DOCKER_TOKEN=<dockerhub_access_token>
```

## Local Development Setup

### Backend Linting & Testing

```bash
cd backend

# Install dev dependencies
pip install -r requirements/development.txt

# Run linting
flake8 apps/ config/
black --check apps/ config/
isort --check-only apps/ config/

# Fix formatting
black apps/ config/
isort apps/ config/

# Run tests
python manage.py test

# Run tests with coverage
coverage run --source='apps' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Frontend Linting & Testing

```bash
cd frontend

# Install dependencies
npm install

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Docker Compose Files

### Development: `docker-compose.yml`
```bash
docker-compose up -d
```

### Staging: `docker-compose.staging.yml`
```bash
docker-compose -f docker-compose.staging.yml up -d
```

### Production: `docker-compose.prod.yml`
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Deployment Process

### Staging Deployment (Automatic)

1. Merge PR to `main` branch
2. CI/CD pipeline runs automatically
3. All tests must pass
4. Docker images built
5. **Automatic deployment to staging**
6. Team notified via Slack

### Production Deployment (Manual Approval)

1. Verify staging deployment successful
2. Navigate to GitHub Actions
3. Click on production deployment job
4. Click "Review deployments"
5. Select "production" environment
6. Click "Approve and deploy"
7. Monitor deployment progress
8. Verify smoke tests pass
9. Team notified via Slack

## Rollback Procedure

### Quick Rollback (Docker)

```bash
# SSH to server
ssh deploy@erp.ikodio.com

# Navigate to project directory
cd /var/www/ikodio-erp-production

# Checkout previous commit
git log --oneline  # Find previous working commit
git checkout <previous_commit_hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml restart
```

### Database Rollback

```bash
# SSH to server
ssh deploy@erp.ikodio.com

# Navigate to project
cd /var/www/ikodio-erp-production

# Rollback last migration
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate <app_name> <previous_migration_number>

# Example: Rollback hr module to migration 0003
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate hr 0003
```

## Monitoring & Alerts

### Health Checks

**Backend:** `https://erp.ikodio.com/api/v1/health/`

**Frontend:** `https://erp.ikodio.com/`

### Slack Notifications

Automatic notifications sent to Slack for:
- ✅ Successful deployments
- ❌ Failed deployments
- ⚠️ Security scan warnings

### Monitoring Tools (Recommended)

- **Application Monitoring:** Sentry, New Relic, or DataDog
- **Infrastructure Monitoring:** Prometheus + Grafana
- **Log Aggregation:** ELK Stack or Loki
- **Uptime Monitoring:** UptimeRobot or Pingdom

## Troubleshooting

### Pipeline Fails on Backend Tests

1. Check test logs in GitHub Actions
2. Reproduce locally: `python manage.py test`
3. Check database migrations: `python manage.py showmigrations`
4. Verify environment variables

### Pipeline Fails on Frontend Build

1. Check build logs in GitHub Actions
2. Reproduce locally: `npm run build`
3. Check TypeScript errors: `npm run type-check`
4. Verify dependencies: `npm ci`

### Deployment Fails on SSH

1. Verify SSH key is added to server: `~/.ssh/authorized_keys`
2. Test SSH connection: `ssh deploy@erp.ikodio.com`
3. Check GitHub secrets are correctly set
4. Verify firewall allows SSH from GitHub Actions IPs

### Deployment Succeeds but Site Down

1. Check Docker containers: `docker-compose ps`
2. Check logs: `docker-compose logs backend frontend`
3. Verify database connection: `docker-compose exec backend python manage.py check --database default`
4. Check Nginx configuration: `sudo nginx -t`
5. Restart services: `docker-compose restart`

## Best Practices

### Commit Messages

Follow conventional commits:
```
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add tests for HR module
chore: update dependencies
```

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes and commit
3. Push to GitHub
4. Create Pull Request to `develop`
5. Wait for CI checks to pass
6. Request code review
7. Merge after approval
8. Delete feature branch

### Release Process

1. Merge `develop` to `main`
2. Tag release: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. Push tag: `git push origin v1.0.0`
4. Create GitHub Release with changelog
5. Deploy to staging (automatic)
6. Test thoroughly on staging
7. Approve production deployment (manual)
8. Monitor production deployment

## Security Considerations

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for sensitive data
3. **Rotate SSH keys** regularly
4. **Enable 2FA** on GitHub accounts
5. **Review security scans** regularly
6. **Update dependencies** monthly
7. **Audit access logs** weekly

## Performance Optimization

1. **Docker Layer Caching** - GitHub Actions cache enabled
2. **Parallel Jobs** - Backend and frontend tests run in parallel
3. **Incremental Builds** - Only changed files rebuilt
4. **Dependency Caching** - pip and npm caches enabled

## Cost Estimation

### GitHub Actions Minutes (Free tier: 2000 min/month)

- Backend tests: ~8 minutes
- Frontend tests: ~5 minutes
- Docker build: ~4 minutes
- **Total per run:** ~17 minutes

**Monthly usage (assuming 100 pushes):**
- 100 runs × 17 minutes = 1,700 minutes/month
- **Fits within free tier** ✅

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

---

**Last Updated:** November 3, 2025  
**Maintained By:** iKodio DevOps Team  
**Contact:** devops@ikodio.com

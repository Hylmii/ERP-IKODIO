# Ikodio ERP System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Django](https://img.shields.io/badge/django-5.0+-green.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)

Comprehensive Enterprise Resource Planning (ERP) system built for IT companies, featuring modular architecture with Django REST Framework backend and React frontend.

## 🚀 Features

### Core Modules
- **HR & Talent Management**: Employee data, attendance, payroll, BPJS, KPI/OKR, recruitment, training
- **Project Management**: Task management, resource allocation, timesheet, Gantt charts, costing
- **Finance & Accounting**: GL, AP/AR, budgeting, invoicing, tax management (PPH/PPN)
- **Sales & CRM**: Lead tracking, client management, quotations, contracts
- **IT Asset Management**: Asset register, licenses, procurement, maintenance
- **Helpdesk System**: Ticketing, SLA tracking, support management
- **Document Management**: Version control, digital signatures, workflows
- **Business Intelligence**: Dashboards, analytics, KPI tracking

### Technical Features
- ✅ RESTful API with Django REST Framework
- ✅ JWT Authentication with RBAC
- ✅ PostgreSQL Database
- ✅ React + Tailwind CSS Frontend
- ✅ Modular Architecture
- ✅ API Documentation (Swagger/OpenAPI)
- ✅ Audit Trail System
- ✅ Inter-module Integration

## 📁 Project Structure

```
ikodio-erp/
├── backend/                  # Django REST Framework Backend
│   ├── config/              # Project configuration
│   ├── apps/                # Django apps (modules)
│   │   ├── core/           # Core utilities and base models
│   │   ├── authentication/ # Auth & user management
│   │   ├── hr/             # HR & Talent Management
│   │   ├── project/        # Project Management System
│   │   ├── finance/        # Finance & Accounting
│   │   ├── crm/            # Sales & CRM
│   │   ├── asset/          # IT Asset Management
│   │   ├── helpdesk/       # Support & Ticketing
│   │   ├── dms/            # Document Management
│   │   └── analytics/      # BI & Analytics
│   ├── requirements/        # Python dependencies
│   └── manage.py
├── frontend/                # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── features/       # Feature-based modules
│   │   ├── layouts/        # Layout components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   └── utils/          # Utility functions
│   └── package.json
├── docker/                  # Docker configurations
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## 🛠️ Tech Stack

### Backend
- Python 3.11+
- Django 5.0+
- Django REST Framework 3.14+
- PostgreSQL 15+
- Redis (caching & sessions)
- Celery (async tasks)

### Frontend
- React 18+
- Tailwind CSS 3+
- React Router v6
- Zustand (state management)
- Axios
- Chart.js / Recharts
- React Query

### DevOps
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm/yarn
- PostgreSQL 15+
- Redis 7+
- Git

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/ikodio/ikodio-erp.git
cd ikodio-erp
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend API URL

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. Using Docker (Recommended for Production)

```bash
# Build and run all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- API Schema: `http://localhost:8000/api/schema/`

## 🔐 Default Credentials

**Admin User** (after createsuperuser):
- Email: admin@ikodio.com
- Password: (as set during createsuperuser)

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
python manage.py test
# or with coverage
pytest --cov=apps
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 📦 Database Configuration

### Remote PostgreSQL Server
```env
DB_HOST=192.168.0.100
DB_PORT=5432
DB_NAME=ikodio_erp
DB_USER=ikodioxlapo
DB_PASSWORD=your_password

# SSH Tunnel (if needed)
ssh -p 7420 -L 5432:localhost:5432 ikodioxlapo@192.168.0.100
```

## 🔧 Development

### Backend Development
```bash
# Create new Django app
python manage.py startapp new_module apps/new_module

# Make migrations
python manage.py makemigrations

# Run shell
python manage.py shell

# Run Celery worker
celery -A config worker -l info
```

### Frontend Development
```bash
# Add new dependency
npm install package-name

# Build for production
npm run build

# Lint and format
npm run lint
npm run format
```

## 📊 Module Integration Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│     HR      │─────▶│   Project    │─────▶│   Finance   │
│  (Employee) │      │ (Allocation) │      │  (Payroll)  │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │                      │
       ▼                     ▼                      ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│     CRM     │      │   Helpdesk   │      │     DMS     │
│  (Clients)  │      │  (Tickets)   │      │ (Documents) │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │                      │
       └─────────────────────┴──────────────────────┘
                             │
                      ┌──────▼───────┐
                      │  Analytics   │
                      │ (Dashboard)  │
                      └──────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software owned by Ikodio.

## 👥 Team

- **Development Team**: Ikodio Engineering
- **Project Manager**: TBD
- **Tech Lead**: TBD

## 📞 Support

For support and questions:
- Email: support@ikodio.com
- Documentation: [docs/](./docs/)
- Issue Tracker: GitHub Issues

## 🗺️ Roadmap

- [x] Phase 1: Project setup and core architecture
- [ ] Phase 2: Core modules (HR, Project, Finance)
- [ ] Phase 3: Supporting modules (CRM, Asset, Helpdesk, DMS)
- [ ] Phase 4: Analytics and BI
- [ ] Phase 5: Mobile app
- [ ] Phase 6: Advanced features (AI/ML integration)

---

**Built with ❤️ by Ikodio Team**

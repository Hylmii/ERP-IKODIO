# Ikodio ERP - Copilot Instructions

## Project Overview
Comprehensive Enterprise Resource Planning (ERP) system for Ikodio IT Company.

## Technology Stack
- **Backend**: Django REST Framework (Python 3.11+)
- **Frontend**: React 18+ with Tailwind CSS
- **Database**: PostgreSQL (Remote Server)
- **Authentication**: JWT with Role-Based Access Control
- **Architecture**: Modular Monorepo

## Core Modules
1. HR & Talent Management
2. Project Management System (PMS)
3. Finance & Accounting
4. Sales & CRM
5. IT Asset & Inventory Management
6. Helpdesk/Support/Ticketing
7. Document Management System (DMS)
8. Business Intelligence Dashboard
9. Security & Access Management

## Development Guidelines
- Follow Django best practices for modular apps
- Use Django REST Framework serializers and viewsets
- Implement proper error handling and validation
- Use PostgreSQL-specific features when beneficial
- Follow React hooks and functional components
- Use Tailwind CSS utility classes
- Implement proper API versioning
- All endpoints must have proper authentication and authorization
- Follow RESTful API design principles
- Write comprehensive tests for all modules

## Database
- Remote PostgreSQL server: ssh -p 7420 ikodioxlapo@192.168.0.100
- Use Django migrations for schema management
- Implement proper foreign key relationships between modules
- Use database indexes for performance

## Security
- JWT token-based authentication
- Role-based access control (RBAC)
- Audit trail for all critical operations
- Input validation and sanitization
- CORS configuration
- Rate limiting on API endpoints

## Project Status
✅ Initial setup in progress

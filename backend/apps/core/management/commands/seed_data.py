"""
Management command to seed the database with sample data for testing.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from apps.authentication.models import User, Role, Permission
from apps.hr.models import Employee, Department, Position, Attendance, Leave, Payroll
from apps.project.models import Project, Task, Sprint
from apps.finance.models import Invoice, Payment, Expense, Budget
from apps.crm.models import Client, Lead, Opportunity
from apps.asset.models import Asset, AssetCategory, Vendor
from apps.helpdesk.models import Ticket, SLAPolicy
from apps.dms.models import Document, DocumentCategory


class Command(BaseCommand):
    help = 'Seed database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Seeding database with sample data...')
        
        # Seed in order of dependencies
        self.seed_auth()
        self.seed_hr()
        self.seed_project()
        self.seed_finance()
        self.seed_crm()
        self.seed_asset()
        self.seed_helpdesk()
        self.seed_dms()

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def clear_data(self):
        """Clear existing data (keep superuser)"""
        models_to_clear = [
            Document, Ticket, Asset, Opportunity, Lead, Client,
            Budget, Expense, Payment, Invoice, Task, Sprint, Project,
            Payroll, Leave, Attendance, Employee, Department, Position
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
        
        # Clear roles and permissions (but not superuser)
        Role.objects.all().delete()
        Permission.objects.all().delete()
        
        # Keep superuser, delete others
        User.objects.filter(is_superuser=False).delete()

    def seed_auth(self):
        """Seed authentication data"""
        self.stdout.write('Seeding users and roles...')
        
        # Create permissions
        perms = []
        resources = ['employee', 'attendance', 'payroll', 'leave', 'project', 'task', 
                    'client', 'invoice', 'expense', 'asset', 'ticket', 'document']
        actions = ['create', 'read', 'update', 'delete']
        
        for resource in resources:
            for action in actions:
                perm, created = Permission.objects.get_or_create(
                    resource=resource,
                    action=action,
                    defaults={'code': f'{resource}_{action}', 'description': f'Can {action} {resource}'}
                )
                perms.append(perm)
        
        # Create roles
        admin_role, _ = Role.objects.get_or_create(
            code='ADMIN',
            defaults={'name': 'Administrator', 'description': 'Full system access', 'is_system_role': True}
        )
        admin_role.permissions.set(perms)
        
        manager_role, _ = Role.objects.get_or_create(
            code='MANAGER',
            defaults={'name': 'Manager', 'description': 'Management access'}
        )
        manager_role.permissions.set(perms[:len(perms)//2])
        
        employee_role, _ = Role.objects.get_or_create(
            code='EMPLOYEE',
            defaults={'name': 'Employee', 'description': 'Basic employee access'}
        )
        employee_role.permissions.set([p for p in perms if p.action == 'read'])
        
        # Create users
        users = [
            {'email': 'manager@ikodio.com', 'first_name': 'John', 'last_name': 'Manager', 'role': manager_role},
            {'email': 'employee1@ikodio.com', 'first_name': 'Alice', 'last_name': 'Smith', 'role': employee_role},
            {'email': 'employee2@ikodio.com', 'first_name': 'Bob', 'last_name': 'Wilson', 'role': employee_role},
            {'email': 'hr@ikodio.com', 'first_name': 'Sarah', 'last_name': 'HR', 'role': manager_role},
        ]
        
        for user_data in users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={**user_data, 'is_active': True}
            )
            if created:
                user.set_password('password123')
                user.save()

    def seed_hr(self):
        """Seed HR data"""
        self.stdout.write('Seeding HR data...')
        
        # Create departments
        departments = [
            {'name': 'Engineering', 'code': 'ENG'},
            {'name': 'Sales', 'code': 'SAL'},
            {'name': 'Marketing', 'code': 'MKT'},
            {'name': 'Finance', 'code': 'FIN'},
            {'name': 'HR', 'code': 'HR'},
        ]
        
        dept_objects = []
        for dept_data in departments:
            dept, _ = Department.objects.get_or_create(**dept_data)
            dept_objects.append(dept)
        
        # Create positions
        positions = [
            {
                'title': 'Software Engineer', 
                'code': 'SE', 
                'level': 'junior',
                'department': dept_objects[0],
                'min_salary': 50000.00,
                'max_salary': 80000.00,
            },
            {
                'title': 'Senior Engineer', 
                'code': 'SNR_ENG', 
                'level': 'senior',
                'department': dept_objects[0],
                'min_salary': 80000.00,
                'max_salary': 120000.00,
            },
            {
                'title': 'Sales Manager', 
                'code': 'SM', 
                'level': 'manager',
                'department': dept_objects[1],
                'min_salary': 60000.00,
                'max_salary': 100000.00,
            },
            {
                'title': 'Marketing Specialist', 
                'code': 'MKT_SPEC', 
                'level': 'junior',
                'department': dept_objects[2],
                'min_salary': 45000.00,
                'max_salary': 70000.00,
            },
            {
                'title': 'Accountant', 
                'code': 'ACC', 
                'level': 'junior',
                'department': dept_objects[3],
                'min_salary': 50000.00,
                'max_salary': 75000.00,
            },
        ]
        
        pos_objects = []
        for pos_data in positions:
            pos, _ = Position.objects.get_or_create(
                code=pos_data['code'],
                defaults=pos_data
            )
            pos_objects.append(pos)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(dept_objects)} departments and {len(pos_objects)} positions'))

    def seed_project(self):
        """Seed project data"""
        self.stdout.write('Seeding project data...')
        
        # Create projects
        projects_data = [
            {'code': 'PRJ001', 'name': 'ERP System Development', 'status': 'in_progress'},
            {'code': 'PRJ002', 'name': 'Mobile App', 'status': 'planning'},
            {'code': 'PRJ003', 'name': 'Website Redesign', 'status': 'in_progress'},
        ]
        
        proj_objects = []
        for proj_data in projects_data:
            proj, _ = Project.objects.get_or_create(
                code=proj_data['code'],
                defaults={
                    **proj_data,
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=90)
                }
            )
            proj_objects.append(proj)
        
        # Create tasks
        statuses = ['todo', 'in_progress', 'review', 'done']
        priorities = ['low', 'medium', 'high']
        
        for i, proj in enumerate(proj_objects):
            for j in range(10):
                Task.objects.get_or_create(
                    project=proj,
                    title=f'Task {j+1} for {proj.name}',
                    defaults={
                        'description': f'Description for task {j+1}',
                        'status': random.choice(statuses),
                        'priority': random.choice(priorities),
                        'due_date': timezone.now().date() + timedelta(days=random.randint(1, 30))
                    }
                )

    def seed_finance(self):
        """Seed finance data"""
        self.stdout.write('Seeding finance data...')
        
        # Create clients first for invoices
        clients = Client.objects.all()
        if not clients.exists():
            self.seed_crm()  # Create clients first
            clients = Client.objects.all()
        
        # Create invoices
        for i, client in enumerate(clients[:5]):
            invoice, _ = Invoice.objects.get_or_create(
                invoice_number=f'INV-2025-{str(i+1).zfill(4)}',
                defaults={
                    'client': client,
                    'issue_date': timezone.now().date(),
                    'due_date': timezone.now().date() + timedelta(days=30),
                    'subtotal': Decimal(f'{random.randint(5, 50)}000000'),
                    'tax': Decimal(f'{random.randint(5, 50) * 1100}'),
                    'total': Decimal(f'{random.randint(5, 50) * 11100}'),
                    'status': random.choice(['draft', 'sent', 'paid'])
                }
            )

    def seed_crm(self):
        """Seed CRM data"""
        self.stdout.write('Seeding CRM data...')
        
        # Create clients
        clients_data = [
            {'code': 'CL001', 'name': 'Acme Corporation', 'email': 'contact@acme.com', 'phone': '+62 812 3456 7890'},
            {'code': 'CL002', 'name': 'Tech Solutions Inc', 'email': 'info@techsol.com', 'phone': '+62 813 4567 8901'},
            {'code': 'CL003', 'name': 'Global Industries', 'email': 'hello@global.com', 'phone': '+62 814 5678 9012'},
            {'code': 'CL004', 'name': 'Digital Dynamics', 'email': 'sales@digidyn.com', 'phone': '+62 815 6789 0123'},
            {'code': 'CL005', 'name': 'Innovate Labs', 'email': 'contact@innovate.com', 'phone': '+62 816 7890 1234'},
        ]
        
        for client_data in clients_data:
            Client.objects.get_or_create(
                code=client_data['code'],
                defaults=client_data
            )
        
        # Create leads
        leads_data = [
            {'name': 'Potential Client A', 'email': 'client.a@example.com', 'status': 'new'},
            {'name': 'Potential Client B', 'email': 'client.b@example.com', 'status': 'contacted'},
            {'name': 'Potential Client C', 'email': 'client.c@example.com', 'status': 'qualified'},
        ]
        
        for lead_data in leads_data:
            Lead.objects.get_or_create(
                email=lead_data['email'],
                defaults=lead_data
            )

    def seed_asset(self):
        """Seed asset data"""
        self.stdout.write('Seeding asset data...')
        
        # Create categories
        categories_data = [
            {'name': 'Laptop', 'code': 'LAP'},
            {'name': 'Monitor', 'code': 'MON'},
            {'name': 'Mobile Device', 'code': 'MOB'},
        ]
        
        cat_objects = []
        for cat_data in categories_data:
            cat, _ = AssetCategory.objects.get_or_create(**cat_data)
            cat_objects.append(cat)
        
        # Create vendors
        vendor, _ = Vendor.objects.get_or_create(
            name='Tech Vendor Inc',
            defaults={'contact_email': 'sales@techvendor.com'}
        )
        
        # Create assets
        assets_data = [
            {'code': 'AST001', 'name': 'MacBook Pro 16"', 'category': cat_objects[0], 'status': 'in_use'},
            {'code': 'AST002', 'name': 'Dell Monitor 27"', 'category': cat_objects[1], 'status': 'in_use'},
            {'code': 'AST003', 'name': 'iPhone 15 Pro', 'category': cat_objects[2], 'status': 'in_use'},
            {'code': 'AST004', 'name': 'MacBook Air', 'category': cat_objects[0], 'status': 'available'},
            {'code': 'AST005', 'name': 'LG Monitor', 'category': cat_objects[1], 'status': 'maintenance'},
        ]
        
        for asset_data in assets_data:
            Asset.objects.get_or_create(
                code=asset_data['code'],
                defaults=asset_data
            )

    def seed_helpdesk(self):
        """Seed helpdesk data"""
        self.stdout.write('Seeding helpdesk data...')
        
        # Create SLA Policy
        sla, _ = SLAPolicy.objects.get_or_create(
            name='Standard SLA',
            defaults={
                'priority': 'medium',
                'response_time_hours': 4,
                'resolution_time_hours': 24
            }
        )
        
        # Create tickets
        tickets_data = [
            {'title': 'Cannot login to system', 'priority': 'high', 'status': 'open'},
            {'title': 'Printer not working', 'priority': 'medium', 'status': 'in_progress'},
            {'title': 'Request new software license', 'priority': 'low', 'status': 'pending'},
            {'title': 'Email not receiving', 'priority': 'high', 'status': 'open'},
            {'title': 'VPN connection issue', 'priority': 'medium', 'status': 'resolved'},
        ]
        
        for i, ticket_data in enumerate(tickets_data):
            Ticket.objects.get_or_create(
                ticket_number=f'TKT-{str(i+1).zfill(5)}',
                defaults={
                    **ticket_data,
                    'description': f'Description for {ticket_data["title"]}',
                    'sla_policy': sla
                }
            )

    def seed_dms(self):
        """Seed DMS data"""
        self.stdout.write('Seeding DMS data...')
        
        # Create categories
        categories_data = [
            {'name': 'Policy', 'code': 'POL'},
            {'name': 'Proposal', 'code': 'PRO'},
            {'name': 'Finance', 'code': 'FIN'},
            {'name': 'Legal', 'code': 'LEG'},
        ]
        
        cat_objects = []
        for cat_data in categories_data:
            cat, _ = DocumentCategory.objects.get_or_create(**cat_data)
            cat_objects.append(cat)
        
        # Create documents
        documents_data = [
            {'title': 'Employee Handbook 2025', 'category': cat_objects[0], 'status': 'approved'},
            {'title': 'Project Proposal - ERP System', 'category': cat_objects[1], 'status': 'pending'},
            {'title': 'Q4 Financial Report', 'category': cat_objects[2], 'status': 'approved'},
            {'title': 'Software License Agreement', 'category': cat_objects[3], 'status': 'approved'},
        ]
        
        for doc_data in documents_data:
            Document.objects.get_or_create(
                title=doc_data['title'],
                defaults={
                    **doc_data,
                    'file_path': f'/documents/{doc_data["title"].lower().replace(" ", "_")}.pdf',
                    'version': '1.0'
                }
            )

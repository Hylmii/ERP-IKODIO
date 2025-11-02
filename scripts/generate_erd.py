#!/usr/bin/env python
"""
Generate Entity Relationship Diagram (ERD) from Django models
Uses django-extensions graph_models command to create visual ERD

Requirements:
    pip install django-extensions pygraphviz

Usage:
    python scripts/generate_erd.py

Output:
    - docs/erd_full.png          # Complete ERD (all modules)
    - docs/erd_auth.png          # Authentication module only
    - docs/erd_hr.png            # HR module only
    - docs/erd_project.png       # Project module only
    - docs/erd_finance.png       # Finance module only
    - docs/erd_crm.png           # CRM module only
    - docs/erd_asset.png         # Asset module only
    - docs/erd_helpdesk.png      # Helpdesk module only
    - docs/erd_dms.png           # DMS module only
    - docs/erd_analytics.png     # Analytics module only
"""

import os
import sys
import django
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command


def generate_erd(app_labels=None, output_file='docs/erd.png', graph_models_args=None):
    """
    Generate ERD using django-extensions graph_models command
    
    Args:
        app_labels: List of app labels to include (None = all apps)
        output_file: Output file path
        graph_models_args: Additional arguments for graph_models command
    """
    if graph_models_args is None:
        graph_models_args = []
    
    args = [
        '--output', output_file,
        '--pygraphviz',
        '--theme', 'django2018',
        '--arrow-shape', 'normal',
        '--group-models',
    ] + graph_models_args
    
    if app_labels:
        args.extend(app_labels)
    else:
        args.append('--all-applications')
    
    print(f"Generating ERD: {output_file}")
    call_command('graph_models', *args)
    print(f"✓ Generated: {output_file}")


def main():
    """Generate all ERD variants"""
    
    # Create docs directory if it doesn't exist
    docs_dir = Path(__file__).resolve().parent.parent / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("iKodio ERP - Entity Relationship Diagram Generator")
    print("=" * 80)
    print()
    
    # Check if django-extensions is installed
    try:
        import django_extensions
    except ImportError:
        print("ERROR: django-extensions is not installed")
        print("Install it with: pip install django-extensions pygraphviz")
        sys.exit(1)
    
    # 1. Full ERD (all modules)
    print("1. Generating FULL ERD (all modules)...")
    generate_erd(
        output_file=str(docs_dir / 'erd_full.png'),
        graph_models_args=[
            '--exclude-models', 'ContentType,Permission,Session,LogEntry',
            '--exclude-columns', 'id',
        ]
    )
    print()
    
    # 2. Authentication Module
    print("2. Generating Authentication Module ERD...")
    generate_erd(
        app_labels=['authentication'],
        output_file=str(docs_dir / 'erd_auth.png')
    )
    print()
    
    # 3. HR Module
    print("3. Generating HR Module ERD...")
    generate_erd(
        app_labels=['hr'],
        output_file=str(docs_dir / 'erd_hr.png')
    )
    print()
    
    # 4. Project Module
    print("4. Generating Project Module ERD...")
    generate_erd(
        app_labels=['project'],
        output_file=str(docs_dir / 'erd_project.png')
    )
    print()
    
    # 5. Finance Module
    print("5. Generating Finance Module ERD...")
    generate_erd(
        app_labels=['finance'],
        output_file=str(docs_dir / 'erd_finance.png')
    )
    print()
    
    # 6. CRM Module
    print("6. Generating CRM Module ERD...")
    generate_erd(
        app_labels=['crm'],
        output_file=str(docs_dir / 'erd_crm.png')
    )
    print()
    
    # 7. Asset Module
    print("7. Generating Asset Module ERD...")
    generate_erd(
        app_labels=['asset'],
        output_file=str(docs_dir / 'erd_asset.png')
    )
    print()
    
    # 8. Helpdesk Module
    print("8. Generating Helpdesk Module ERD...")
    generate_erd(
        app_labels=['helpdesk'],
        output_file=str(docs_dir / 'erd_helpdesk.png')
    )
    print()
    
    # 9. DMS Module
    print("9. Generating DMS Module ERD...")
    generate_erd(
        app_labels=['dms'],
        output_file=str(docs_dir / 'erd_dms.png')
    )
    print()
    
    # 10. Analytics Module
    print("10. Generating Analytics Module ERD...")
    generate_erd(
        app_labels=['analytics'],
        output_file=str(docs_dir / 'erd_analytics.png')
    )
    print()
    
    # 11. Core Business Modules (HR + Project + Finance)
    print("11. Generating Core Business ERD...")
    generate_erd(
        app_labels=['hr', 'project', 'finance'],
        output_file=str(docs_dir / 'erd_core_business.png')
    )
    print()
    
    # 12. Customer Facing Modules (CRM + Helpdesk + DMS)
    print("12. Generating Customer Facing ERD...")
    generate_erd(
        app_labels=['crm', 'helpdesk', 'dms'],
        output_file=str(docs_dir / 'erd_customer_facing.png')
    )
    print()
    
    print("=" * 80)
    print("✓ All ERD diagrams generated successfully!")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  - docs/erd_full.png (Complete system)")
    print("  - docs/erd_auth.png (Authentication)")
    print("  - docs/erd_hr.png (HR)")
    print("  - docs/erd_project.png (Project)")
    print("  - docs/erd_finance.png (Finance)")
    print("  - docs/erd_crm.png (CRM)")
    print("  - docs/erd_asset.png (Asset)")
    print("  - docs/erd_helpdesk.png (Helpdesk)")
    print("  - docs/erd_dms.png (DMS)")
    print("  - docs/erd_analytics.png (Analytics)")
    print("  - docs/erd_core_business.png (HR + Project + Finance)")
    print("  - docs/erd_customer_facing.png (CRM + Helpdesk + DMS)")
    print()


if __name__ == '__main__':
    main()

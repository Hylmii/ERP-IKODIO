#!/usr/bin/env python
"""
Simple ERD Generator for iKodio ERP
Creates text-based ERD documentation by inspecting Django models
"""

import os
import sys
import django
from pathlib import Path
from collections import defaultdict

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.db import models


def get_field_info(field):
    """Extract field information"""
    info = {
        'name': field.name,
        'type': field.get_internal_type(),
        'null': field.null,
        'blank': field.blank,
        'unique': field.unique if hasattr(field, 'unique') else False,
        'primary_key': field.primary_key,
    }
    
    # Foreign Key information
    if isinstance(field, models.ForeignKey):
        info['related_model'] = field.related_model.__name__
        info['related_app'] = field.related_model._meta.app_label
    
    # Many-to-Many information
    if isinstance(field, models.ManyToManyField):
        info['related_model'] = field.related_model.__name__
        info['related_app'] = field.related_model._meta.app_label
    
    return info


def generate_model_summary(app_label):
    """Generate summary for all models in an app"""
    app_config = apps.get_app_config(app_label)
    models_list = list(app_config.get_models())  # Convert generator to list
    
    summary = []
    summary.append(f"\n## {app_label.upper()} Module\n")
    summary.append(f"**Total Models:** {len(models_list)}\n")
    
    for model in models_list:
        summary.append(f"\n### {model.__name__}")
        summary.append(f"**Table:** `{model._meta.db_table}`\n")
        
        # Fields
        summary.append("**Fields:**")
        for field in model._meta.fields:
            field_info = get_field_info(field)
            field_str = f"- `{field_info['name']}`: {field_info['type']}"
            
            if field_info['primary_key']:
                field_str += " (PK)"
            elif isinstance(field, models.ForeignKey):
                field_str += f" → {field_info['related_app']}.{field_info['related_model']}"
            
            if field_info['unique']:
                field_str += " (UNIQUE)"
            if field_info['null']:
                field_str += " (NULL)"
                
            summary.append(field_str)
        
        # Relationships
        fks = [f for f in model._meta.fields if isinstance(f, models.ForeignKey)]
        m2ms = [f for f in model._meta.many_to_many]
        
        if fks:
            summary.append("\n**Foreign Keys:**")
            for fk in fks:
                related_model = fk.related_model
                summary.append(f"- {fk.name} → {related_model._meta.app_label}.{related_model.__name__}")
        
        if m2ms:
            summary.append("\n**Many-to-Many:**")
            for m2m in m2ms:
                related_model = m2m.related_model
                summary.append(f"- {m2m.name} ↔ {related_model._meta.app_label}.{related_model.__name__}")
        
        summary.append("")
    
    return "\n".join(summary)


def main():
    """Generate ERD documentation"""
    
    print("=" * 80)
    print("iKodio ERP - ERD Generator")
    print("=" * 80)
    print()
    
    # List of apps to document
    apps_to_document = [
        'authentication',
        'hr',
        'project',
        'finance',
        'crm',
        'asset',
        'helpdesk',
        'dms',
        'analytics',
    ]
    
    output_file = Path(__file__).resolve().parent.parent / 'docs' / 'ERD_DETAILED.md'
    
    with open(output_file, 'w') as f:
        f.write("# iKodio ERP - Detailed Entity Relationship Diagram\n\n")
        f.write(f"**Generated:** {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## Table of Contents\n\n")
        
        for app in apps_to_document:
            f.write(f"- [{app.upper()} Module](#{app}-module)\n")
        
        f.write("\n---\n")
        
        # Generate detailed documentation for each app
        total_models = 0
        for app in apps_to_document:
            print(f"Processing {app} module...")
            summary = generate_model_summary(app)
            f.write(summary)
            
            app_config = apps.get_app_config(app)
            total_models += len(list(app_config.get_models()))
        
        f.write(f"\n\n---\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Modules:** {len(apps_to_document)}\n")
        f.write(f"- **Total Models:** {total_models}\n")
        f.write(f"- **Database:** PostgreSQL 15+\n")
        f.write(f"- **ORM:** Django ORM\n")
    
    print()
    print("=" * 80)
    print(f"✓ ERD Documentation Generated: {output_file}")
    print(f"✓ Total Models Documented: {total_models}")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()

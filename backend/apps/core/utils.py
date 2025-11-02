"""
Utility functions and helpers
"""
import hashlib
import random
import string
from datetime import datetime


def generate_unique_code(prefix='', length=8):
    """Generate unique code with optional prefix"""
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"{prefix}{timestamp}{random_string}" if prefix else f"{timestamp}{random_string}"


def generate_file_hash(file_obj):
    """Generate SHA256 hash for uploaded file"""
    sha256_hash = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def format_currency(amount, currency='IDR'):
    """Format amount as currency string"""
    if currency == 'IDR':
        return f"Rp {amount:,.0f}"
    return f"{currency} {amount:,.2f}"


def calculate_pagination_info(paginator, page):
    """Calculate pagination metadata"""
    return {
        'total_items': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page.number,
        'page_size': paginator.per_page,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
    }

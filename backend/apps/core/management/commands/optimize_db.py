"""
Management command to optimize database performance
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Optimize database performance with indexes and statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze database and update statistics',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Vacuum database (PostgreSQL only)',
        )
        parser.add_argument(
            '--show-indexes',
            action='store_true',
            help='Show all indexes',
        )

    def handle(self, *args, **options):
        if options['show_indexes']:
            self.show_indexes()
        
        if options['analyze']:
            self.analyze_database()
        
        if options['vacuum']:
            self.vacuum_database()

    def show_indexes(self):
        """Show all database indexes"""
        self.stdout.write(self.style.SUCCESS('\n=== Database Indexes ===\n'))
        
        with connection.cursor() as cursor:
            # Get database engine
            engine = connection.settings_dict['ENGINE']
            
            if 'postgresql' in engine:
                cursor.execute("""
                    SELECT
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname;
                """)
                
                current_table = None
                for row in cursor.fetchall():
                    table, index, definition = row
                    
                    if table != current_table:
                        self.stdout.write(f"\n{table}:")
                        current_table = table
                    
                    self.stdout.write(f"  - {index}")
            
            elif 'sqlite' in engine:
                # Get all tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                """)
                
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"PRAGMA index_list('{table}');")
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        self.stdout.write(f"\n{table}:")
                        for idx in indexes:
                            self.stdout.write(f"  - {idx[1]}")

    def analyze_database(self):
        """Analyze database and update statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== Analyzing Database ===\n'))
        
        with connection.cursor() as cursor:
            engine = connection.settings_dict['ENGINE']
            
            if 'postgresql' in engine:
                self.stdout.write('Running ANALYZE on all tables...')
                cursor.execute('ANALYZE;')
                self.stdout.write(self.style.SUCCESS('✓ Analysis complete'))
            
            elif 'sqlite' in engine:
                self.stdout.write('Running ANALYZE on SQLite database...')
                cursor.execute('ANALYZE;')
                self.stdout.write(self.style.SUCCESS('✓ Analysis complete'))
            
            else:
                self.stdout.write(self.style.WARNING('ANALYZE not supported for this database'))

    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize"""
        self.stdout.write(self.style.SUCCESS('\n=== Vacuuming Database ===\n'))
        
        with connection.cursor() as cursor:
            engine = connection.settings_dict['ENGINE']
            
            if 'postgresql' in engine:
                self.stdout.write('Running VACUUM on all tables...')
                # Note: VACUUM cannot run inside a transaction
                connection.set_autocommit(True)
                cursor.execute('VACUUM;')
                connection.set_autocommit(False)
                self.stdout.write(self.style.SUCCESS('✓ Vacuum complete'))
            
            elif 'sqlite' in engine:
                self.stdout.write('Running VACUUM on SQLite database...')
                cursor.execute('VACUUM;')
                self.stdout.write(self.style.SUCCESS('✓ Vacuum complete'))
            
            else:
                self.stdout.write(self.style.WARNING('VACUUM not supported for this database'))

    def get_table_stats(self):
        """Get table statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== Table Statistics ===\n'))
        
        with connection.cursor() as cursor:
            engine = connection.settings_dict['ENGINE']
            
            if 'postgresql' in engine:
                cursor.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        n_live_tup as row_count,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 20;
                """)
                
                self.stdout.write(f"{'Table':<30} {'Rows':>10} {'Size':>12}")
                self.stdout.write('-' * 55)
                
                for row in cursor.fetchall():
                    schema, table, rows, size = row
                    self.stdout.write(f"{table:<30} {rows:>10} {size:>12}")

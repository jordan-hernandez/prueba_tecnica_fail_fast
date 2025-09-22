from django.core.management.base import BaseCommand
from django.db import connection
from inventory.sql_functions import (
    GET_PRODUCTS_BY_BRAND_AND_CUSTOMER_SQL,
    GET_PAYMENTS_BY_PRODUCT_QUANTITY_SQL,
    GET_STOCK_ANALYSIS_SQL,
    GET_TOP_SELLING_PRODUCTS_SQL,
    DROP_FUNCTIONS_SQL
)


class Command(BaseCommand):
    help = 'Gestiona las funciones SQL de PostgreSQL del sistema de inventario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['create', 'drop', 'recreate'],
            default='create',
            help='Acción a realizar con las funciones SQL'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Ejecutar tests de las funciones después de crearlas'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'drop':
            self.drop_functions()
        elif action == 'recreate':
            self.drop_functions()
            self.create_functions()
        else:  # create
            self.create_functions()
        
        if options['test']:
            self.test_functions()

    def create_functions(self):
        """Crea todas las funciones SQL de PostgreSQL"""
        self.stdout.write('Creando funciones SQL de PostgreSQL...')
        
        functions = [
            ('get_products_by_brand_and_customer', GET_PRODUCTS_BY_BRAND_AND_CUSTOMER_SQL),
            ('get_payments_by_product_quantity', GET_PAYMENTS_BY_PRODUCT_QUANTITY_SQL),
            ('get_stock_analysis', GET_STOCK_ANALYSIS_SQL),
            ('get_top_selling_products', GET_TOP_SELLING_PRODUCTS_SQL),
        ]
        
        with connection.cursor() as cursor:
            for func_name, func_sql in functions:
                try:
                    cursor.execute(func_sql)
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Función {func_name} creada exitosamente')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error creando {func_name}: {e}')
                    )

    def drop_functions(self):
        """Elimina todas las funciones SQL"""
        self.stdout.write('Eliminando funciones SQL existentes...')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute(DROP_FUNCTIONS_SQL)
                self.stdout.write(
                    self.style.WARNING('✓ Funciones eliminadas')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error eliminando funciones: {e}')
                )

    def test_functions(self):
        """Prueba que las funciones funcionan correctamente"""
        self.stdout.write('Probando funciones SQL...')
        
        tests = [
            (
                "get_products_by_brand_and_customer('Samsung', 'john@example.com')",
                "Productos Samsung para john@example.com"
            ),
            (
                "get_payments_by_product_quantity('TV-SAMSUNG-001', 1)",
                "Pagos del producto TV-SAMSUNG-001 con cantidad >= 1"
            ),
            (
                "get_stock_analysis('Bodega', 0)",
                "Análisis de stock con filtro 'Bodega'"
            ),
            (
                "get_top_selling_products(5, NULL, NULL)",
                "Top 5 productos más vendidos"
            ),
        ]
        
        with connection.cursor() as cursor:
            for query, description in tests:
                try:
                    cursor.execute(f"SELECT * FROM {query} LIMIT 3")
                    results = cursor.fetchall()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {description}: {len(results)} resultados'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {description}: {e}')
                    )

    def show_function_info(self):
        """Muestra información sobre las funciones existentes"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    routine_name,
                    routine_type,
                    data_type
                FROM information_schema.routines 
                WHERE routine_schema = 'public' 
                AND routine_name LIKE 'get_%'
                ORDER BY routine_name;
            """)
            
            functions = cursor.fetchall()
            
            if functions:
                self.stdout.write('\nFunciones SQL encontradas:')
                for func in functions:
                    self.stdout.write(f'  - {func[0]} ({func[1]})')
            else:
                self.stdout.write('No se encontraron funciones SQL personalizadas') 
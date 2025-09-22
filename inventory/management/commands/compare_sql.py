import time
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from inventory.models import Product, Brand, Customer, Order, OrderItem, Payment


class Command(BaseCommand):
    help = 'Compara el SQL generado por Django ORM con funciones SQL de PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--case',
            type=str,
            choices=['products_by_brand_customer', 'payments_by_quantity', 'all'],
            default='all',
            help='Caso de uso específico a comparar'
        )
        parser.add_argument(
            '--brand-name',
            type=str,
            default='Samsung',
            help='Nombre de marca para la consulta'
        )
        parser.add_argument(
            '--customer-email',
            type=str,
            default='john@example.com',
            help='Email del cliente para la consulta'
        )
        parser.add_argument(
            '--product-sku',
            type=str,
            default='TV-SAMSUNG-001',
            help='SKU del producto para la consulta'
        )
        parser.add_argument(
            '--min-quantity',
            type=int,
            default=5,
            help='Cantidad mínima para la consulta'
        )

    def handle(self, *args, **options):
        case = options['case']
        
        if case in ['products_by_brand_customer', 'all']:
            self.compare_products_by_brand_customer(
                options['brand_name'], 
                options['customer_email']
            )
        
        if case in ['payments_by_quantity', 'all']:
            self.compare_payments_by_quantity(
                options['product_sku'], 
                options['min_quantity']
            )

    def compare_products_by_brand_customer(self, brand_name, customer_email):
        """
        Compara consulta: Productos de una marca que aparecen en órdenes de un cliente
        """
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== COMPARACIÓN: Productos de marca "{brand_name}" en órdenes de "{customer_email}" ==='
            )
        )
        
        # 1. CONSULTA CON DJANGO ORM
        self.stdout.write('\n1. CONSULTA CON DJANGO ORM:')
        
        start_time = time.time()
        
        # Consulta equivalente usando el método get_related
        django_queryset = Product.objects.select_related(
            'brand', 'category'
        ).prefetch_related(
            'order_items__order__customer'
        ).filter(
            brand__name__icontains=brand_name,
            order_items__order__customer__email=customer_email,
            is_active=True,
            brand__is_active=True
        ).distinct()
        
        # Forzar evaluación del queryset
        django_results = list(django_queryset)
        django_time = time.time() - start_time
        
        # Mostrar SQL generado
        self.stdout.write(f'SQL Generado por Django ORM:')
        self.stdout.write(f'{str(django_queryset.query)}')
        self.stdout.write(f'Resultados: {len(django_results)} productos')
        self.stdout.write(f'Tiempo de ejecución: {django_time:.4f} segundos')
        
        # 2. FUNCIÓN SQL DE POSTGRESQL
        self.stdout.write('\n2. FUNCIÓN SQL DE POSTGRESQL:')
        
        start_time = time.time()
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_products_by_brand_and_customer(%s, %s)",
                [brand_name, customer_email]
            )
            sql_results = cursor.fetchall()
            
        sql_time = time.time() - start_time
        
        self.stdout.write(f'Función SQL: get_products_by_brand_and_customer()')
        self.stdout.write(f'Resultados: {len(sql_results)} filas')
        self.stdout.write(f'Tiempo de ejecución: {sql_time:.4f} segundos')
        
        # 3. ANÁLISIS DE DIFERENCIAS
        self.stdout.write('\n3. ANÁLISIS DE DIFERENCIAS:')
        
        self.stdout.write(f'• Diferencia en cantidad de resultados: {len(django_results) - len(sql_results)}')
        self.stdout.write(f'• Diferencia en tiempo: {(django_time - sql_time):.4f} segundos')
        
        if django_time > sql_time:
            percentage = ((django_time - sql_time) / sql_time) * 100
            self.stdout.write(f'• Función SQL es {percentage:.1f}% más rápida')
        else:
            percentage = ((sql_time - django_time) / django_time) * 100
            self.stdout.write(f'• Django ORM es {percentage:.1f}% más rápido')
        
        # 4. COMPLEJIDADES
        self.stdout.write('\n4. ANÁLISIS DE COMPLEJIDAD:')
        self.stdout.write('Django ORM:')
        self.stdout.write('  - Temporal: O(n) + overhead de ORM + múltiples queries (sin optimización)')
        self.stdout.write('  - Espacial: O(n) + objetos Python + cache del ORM')
        self.stdout.write('  - Ventajas: Abstracción, seguridad, portabilidad')
        self.stdout.write('  - Desventajas: Overhead de conversión, posible N+1')
        
        self.stdout.write('Función PostgreSQL:')
        self.stdout.write('  - Temporal: O(n) optimizada por motor de BD')
        self.stdout.write('  - Espacial: O(n) solo resultados, sin overhead')
        self.stdout.write('  - Ventajas: Velocidad, optimización del motor DB')
        self.stdout.write('  - Desventajas: Acoplamiento a PostgreSQL, mantenimiento manual')

    def compare_payments_by_quantity(self, product_sku, min_quantity):
        """
        Compara consulta: Pagos donde se facturó un producto por más de X unidades
        """
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== COMPARACIÓN: Pagos del producto "{product_sku}" con cantidad >= {min_quantity} ==='
            )
        )
        
        # 1. CONSULTA CON DJANGO ORM
        self.stdout.write('\n1. CONSULTA CON DJANGO ORM:')
        
        start_time = time.time()
        
        django_queryset = Payment.objects.select_related(
            'order__customer'
        ).prefetch_related(
            'order__items__product'
        ).filter(
            order__items__product__sku=product_sku,
            order__items__qty__gte=min_quantity,
            status='CONFIRMED'
        ).distinct()
        
        django_results = list(django_queryset)
        django_time = time.time() - start_time
        
        self.stdout.write(f'SQL Generado por Django ORM:')
        self.stdout.write(f'{str(django_queryset.query)}')
        self.stdout.write(f'Resultados: {len(django_results)} pagos')
        self.stdout.write(f'Tiempo de ejecución: {django_time:.4f} segundos')
        
        # 2. FUNCIÓN SQL DE POSTGRESQL
        self.stdout.write('\n2. FUNCIÓN SQL DE POSTGRESQL:')
        
        start_time = time.time()
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_payments_by_product_quantity(%s, %s)",
                [product_sku, min_quantity]
            )
            sql_results = cursor.fetchall()
            
        sql_time = time.time() - start_time
        
        self.stdout.write(f'Función SQL: get_payments_by_product_quantity()')
        self.stdout.write(f'Resultados: {len(sql_results)} filas')
        self.stdout.write(f'Tiempo de ejecución: {sql_time:.4f} segundos')
        
        # 3. ANÁLISIS DE DIFERENCIAS
        self.stdout.write('\n3. ANÁLISIS DE DIFERENCIAS:')
        
        self.stdout.write(f'• Diferencia en cantidad de resultados: {len(django_results) - len(sql_results)}')
        self.stdout.write(f'• Diferencia en tiempo: {(django_time - sql_time):.4f} segundos')
        
        if django_time > sql_time:
            percentage = ((django_time - sql_time) / sql_time) * 100
            self.stdout.write(f'• Función SQL es {percentage:.1f}% más rápida')
        else:
            percentage = ((sql_time - django_time) / django_time) * 100
            self.stdout.write(f'• Django ORM es {percentage:.1f}% más rápido')

    def get_query_plan(self, query):
        """Obtiene el plan de ejecución de una consulta"""
        with connection.cursor() as cursor:
            cursor.execute(f"EXPLAIN ANALYZE {query}")
            return cursor.fetchall() 
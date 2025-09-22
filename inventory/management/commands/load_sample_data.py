from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from inventory.models import (
    Brand, Category, Product, Warehouse, 
    Stock, Customer, Order, OrderItem, Payment
)


class Command(BaseCommand):
    help = 'Carga datos de prueba en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todos los datos existentes antes de cargar'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        self.load_sample_data()
        self.stdout.write(
            self.style.SUCCESS('Datos de prueba cargados exitosamente!')
        )

    def clear_data(self):
        """Elimina todos los datos existentes"""
        self.stdout.write('Eliminando datos existentes...')
        
        # Eliminar en orden correcto (respetando dependencias)
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Stock.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Warehouse.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

    @transaction.atomic
    def load_sample_data(self):
        """Carga datos de prueba"""
        self.stdout.write('Cargando datos de prueba...')
        
        # 1. Crear marcas
        brands = [
            Brand.objects.create(name='Samsung', is_active=True),
            Brand.objects.create(name='LG', is_active=True),
            Brand.objects.create(name='Sony', is_active=True),
            Brand.objects.create(name='Apple', is_active=True),
            Brand.objects.create(name='Xiaomi', is_active=True),
        ]
        self.stdout.write(f'Creadas {len(brands)} marcas')
        
        # 2. Crear categorías
        categories = [
            Category.objects.create(name='Televisores', is_active=True),
            Category.objects.create(name='Smartphones', is_active=True),
            Category.objects.create(name='Laptops', is_active=True),
            Category.objects.create(name='Tablets', is_active=True),
            Category.objects.create(name='Electrodomésticos', is_active=True),
        ]
        self.stdout.write(f'Creadas {len(categories)} categorías')
        
        # 3. Crear productos
        products = [
            # Samsung
            Product.objects.create(
                name='Samsung QLED 55" 4K Smart TV',
                sku='TV-SAMSUNG-001',
                price=Decimal('1299.99'),
                brand=brands[0],  # Samsung
                category=categories[0],  # Televisores
                is_active=True
            ),
            Product.objects.create(
                name='Samsung Galaxy S23 Ultra',
                sku='PHONE-SAMSUNG-001',
                price=Decimal('1199.99'),
                brand=brands[0],
                category=categories[1],  # Smartphones
                is_active=True
            ),
            # LG
            Product.objects.create(
                name='LG OLED 65" 4K Smart TV',
                sku='TV-LG-001',
                price=Decimal('1599.99'),
                brand=brands[1],  # LG
                category=categories[0],
                is_active=True
            ),
            Product.objects.create(
                name='LG Gram 15" Laptop',
                sku='LAPTOP-LG-001',
                price=Decimal('999.99'),
                brand=brands[1],
                category=categories[2],  # Laptops
                is_active=True
            ),
            # Sony
            Product.objects.create(
                name='Sony Bravia 55" 4K HDR TV',
                sku='TV-SONY-001',
                price=Decimal('899.99'),
                brand=brands[2],  # Sony
                category=categories[0],
                is_active=True
            ),
            # Apple
            Product.objects.create(
                name='iPhone 15 Pro Max',
                sku='PHONE-APPLE-001',
                price=Decimal('1499.99'),
                brand=brands[3],  # Apple
                category=categories[1],
                is_active=True
            ),
            Product.objects.create(
                name='MacBook Pro 16"',
                sku='LAPTOP-APPLE-001',
                price=Decimal('2499.99'),
                brand=brands[3],
                category=categories[2],
                is_active=True
            ),
            Product.objects.create(
                name='iPad Pro 12.9"',
                sku='TABLET-APPLE-001',
                price=Decimal('1099.99'),
                brand=brands[3],
                category=categories[3],  # Tablets
                is_active=True
            ),
            # Xiaomi
            Product.objects.create(
                name='Xiaomi Mi TV 43" 4K',
                sku='TV-XIAOMI-001',
                price=Decimal('399.99'),
                brand=brands[4],  # Xiaomi
                category=categories[0],
                is_active=True
            ),
            Product.objects.create(
                name='Xiaomi Redmi Note 12 Pro',
                sku='PHONE-XIAOMI-001',
                price=Decimal('299.99'),
                brand=brands[4],
                category=categories[1],
                is_active=True
            ),
        ]
        self.stdout.write(f'Creados {len(products)} productos')
        
        # 4. Crear bodegas
        warehouses = [
            Warehouse.objects.create(name='Bodega Central', city='Bogotá'),
            Warehouse.objects.create(name='Bodega Norte', city='Medellín'),
            Warehouse.objects.create(name='Bodega Costa', city='Cartagena'),
            Warehouse.objects.create(name='Bodega Sur', city='Cali'),
        ]
        self.stdout.write(f'Creadas {len(warehouses)} bodegas')
        
        # 5. Crear stock
        stocks = []
        stock_quantities = [
            (100, 10), (50, 5), (75, 8), (30, 3), (120, 15),
            (80, 12), (60, 7), (40, 4), (90, 9), (110, 11)
        ]
        
        for i, product in enumerate(products):
            for j, warehouse in enumerate(warehouses):
                qty, reserved = stock_quantities[i]
                # Variar el stock por bodega
                actual_qty = qty + (j * 10)
                actual_reserved = min(reserved + j, actual_qty)
                
                stocks.append(
                    Stock.objects.create(
                        product=product,
                        warehouse=warehouse,
                        qty=actual_qty,
                        reserved=actual_reserved
                    )
                )
        self.stdout.write(f'Creados {len(stocks)} registros de stock')
        
        # 6. Crear clientes
        customers = [
            Customer.objects.create(
                full_name='John Doe',
                email='john@example.com'
            ),
            Customer.objects.create(
                full_name='Jane Smith',
                email='jane@example.com'
            ),
            Customer.objects.create(
                full_name='Carlos Rodriguez',
                email='carlos@example.com'
            ),
            Customer.objects.create(
                full_name='Maria Garcia',
                email='maria@example.com'
            ),
            Customer.objects.create(
                full_name='Luis Fernandez',
                email='luis@example.com'
            ),
        ]
        self.stdout.write(f'Creados {len(customers)} clientes')
        
        # 7. Crear órdenes
        orders = []
        order_data = [
            (customers[0], 'CONFIRMED'),  # John
            (customers[1], 'PENDING'),    # Jane
            (customers[2], 'CONFIRMED'),  # Carlos
            (customers[3], 'CONFIRMED'),  # Maria
            (customers[0], 'PENDING'),    # John (segunda orden)
            (customers[4], 'CONFIRMED'),  # Luis
        ]
        
        for customer, status in order_data:
            orders.append(
                Order.objects.create(
                    customer=customer,
                    status=status
                )
            )
        self.stdout.write(f'Creadas {len(orders)} órdenes')
        
        # 8. Crear items de órdenes
        order_items = []
        
        # Orden 1 (John - CONFIRMED): Samsung TV + Galaxy S23
        order_items.extend([
            OrderItem.objects.create(
                order=orders[0],
                product=products[0],  # Samsung TV
                qty=1,
                unit_price=products[0].price
            ),
            OrderItem.objects.create(
                order=orders[0],
                product=products[1],  # Galaxy S23
                qty=2,
                unit_price=products[1].price
            ),
        ])
        
        # Orden 2 (Jane - PENDING): LG TV
        order_items.append(
            OrderItem.objects.create(
                order=orders[1],
                product=products[2],  # LG TV
                qty=1,
                unit_price=products[2].price
            )
        )
        
        # Orden 3 (Carlos - CONFIRMED): iPhone + iPad
        order_items.extend([
            OrderItem.objects.create(
                order=orders[2],
                product=products[5],  # iPhone
                qty=1,
                unit_price=products[5].price
            ),
            OrderItem.objects.create(
                order=orders[2],
                product=products[7],  # iPad
                qty=1,
                unit_price=products[7].price
            ),
        ])
        
        # Orden 4 (Maria - CONFIRMED): MacBook
        order_items.append(
            OrderItem.objects.create(
                order=orders[3],
                product=products[6],  # MacBook
                qty=1,
                unit_price=products[6].price
            )
        )
        
        # Orden 5 (John segunda - PENDING): Xiaomi TV + Phone
        order_items.extend([
            OrderItem.objects.create(
                order=orders[4],
                product=products[8],  # Xiaomi TV
                qty=3,  # Cantidad alta para testing
                unit_price=products[8].price
            ),
            OrderItem.objects.create(
                order=orders[4],
                product=products[9],  # Xiaomi Phone
                qty=2,
                unit_price=products[9].price
            ),
        ])
        
        # Orden 6 (Luis - CONFIRMED): Samsung TV (para testing Brand+Customer)
        order_items.append(
            OrderItem.objects.create(
                order=orders[5],
                product=products[0],  # Samsung TV
                qty=1,
                unit_price=products[0].price
            )
        )
        
        self.stdout.write(f'Creados {len(order_items)} items de órdenes')
        
        # 9. Crear pagos (solo para órdenes confirmadas)
        payments = []
        payment_methods = ['CARD', 'TRANSFER', 'COD']
        
        for i, order in enumerate(orders):
            if order.status == 'CONFIRMED':
                payments.append(
                    Payment.objects.create(
                        order=order,
                        method=payment_methods[i % len(payment_methods)],
                        amount=order.total_amount,
                        status='CONFIRMED'
                    )
                )
        
        self.stdout.write(f'Creados {len(payments)} pagos')
        
        # Mostrar resumen
        self.stdout.write('\n=== RESUMEN DE DATOS CREADOS ===')
        self.stdout.write(f'Marcas: {Brand.objects.count()}')
        self.stdout.write(f'Categorías: {Category.objects.count()}')
        self.stdout.write(f'Productos: {Product.objects.count()}')
        self.stdout.write(f'Bodegas: {Warehouse.objects.count()}')
        self.stdout.write(f'Stock: {Stock.objects.count()}')
        self.stdout.write(f'Clientes: {Customer.objects.count()}')
        self.stdout.write(f'Órdenes: {Order.objects.count()}')
        self.stdout.write(f'Items de órdenes: {OrderItem.objects.count()}')
        self.stdout.write(f'Pagos: {Payment.objects.count()}')
        
        # Datos específicos para testing
        self.stdout.write('\n=== DATOS PARA TESTING ===')
        self.stdout.write('Para get_related examples:')
        self.stdout.write('- Brand "Samsung" con Customer "john@example.com"')
        self.stdout.write('- Product SKU "TV-SAMSUNG-001" con quantity >= 1')
        self.stdout.write('- Customer "john@example.com" tiene 2 órdenes')
        self.stdout.write('- Warehouse "Bodega Central" en "Bogotá"') 
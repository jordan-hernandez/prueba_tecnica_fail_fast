import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class BaseModel(models.Model):
    """Modelo base con campos comunes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        abstract = True


class Brand(BaseModel):
    """Modelo para las marcas de productos"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Category(BaseModel):
    """Modelo para las categorías de productos"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(BaseModel):
    """Modelo para los productos"""
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField(default=True)
    
    # Relaciones
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.PROTECT,
        related_name='products'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        related_name='products'
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['brand', 'category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


class Warehouse(BaseModel):
    """Modelo para las bodegas"""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"
        ordering = ['city', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Stock(BaseModel):
    """Modelo para el stock de productos en bodegas"""
    qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    reserved = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relaciones
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    
    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'warehouse'],
                name='unique_product_warehouse_stock'
            ),
            models.CheckConstraint(
                check=models.Q(reserved__lte=models.F('qty')),
                name='reserved_lte_qty'
            )
        ]
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.warehouse.name}: {self.qty}"
    
    @property
    def available_qty(self):
        """Cantidad disponible (no reservada)"""
        return self.qty - self.reserved


class Customer(BaseModel):
    """Modelo para los clientes"""
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Order(BaseModel):
    """Modelo para las órdenes de compra"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELED', 'Cancelada'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Relaciones
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT,
        related_name='orders'
    )
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer', 'status']),
        ]
    
    def __str__(self):
        return f"Orden {self.id} - {self.customer.full_name}"
    
    @property
    def total_amount(self):
        """Calcula el monto total de la orden"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        """Calcula el total de items en la orden"""
        return sum(item.qty for item in self.items.all())


class OrderItem(BaseModel):
    """Modelo para los items de una orden"""
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Relaciones
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_product'
            )
        ]
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x{self.qty} - Orden {self.order.id}"
    
    @property
    def total_price(self):
        """Calcula el precio total del item"""
        return self.qty * self.unit_price
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para establecer unit_price del producto si no se especifica"""
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)


class Payment(BaseModel):
    """Modelo para los pagos de las órdenes"""
    
    METHOD_CHOICES = [
        ('CARD', 'Tarjeta'),
        ('TRANSFER', 'Transferencia'),
        ('COD', 'Contra Entrega'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmado'),
        ('FAILED', 'Fallido'),
    ]
    
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Relaciones
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE,
        related_name='payment'
    )
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'method']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Pago {self.method} - ${self.amount} - Orden {self.order.id}" 
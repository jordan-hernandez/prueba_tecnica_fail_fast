from rest_framework import serializers
from .models import (
    Brand, Category, Product, Warehouse, 
    Stock, Customer, Order, OrderItem, Payment
)


class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'is_active', 'created_at', 'products_count']
        read_only_fields = ['id', 'created_at']
    
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at', 'products_count']
        read_only_fields = ['id', 'created_at']
    
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'price', 'is_active', 'created_at',
            'brand', 'brand_name', 'category', 'category_name', 'total_stock'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_total_stock(self, obj):
        return sum(stock.qty for stock in obj.stocks.all())


class WarehouseSerializer(serializers.ModelSerializer):
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'city', 'created_at', 'total_products']
        read_only_fields = ['id', 'created_at']
    
    def get_total_products(self, obj):
        return obj.stocks.filter(qty__gt=0).count()


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    available_qty = serializers.ReadOnlyField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'qty', 'reserved', 'updated_at', 'created_at',
            'product', 'product_name', 'product_sku',
            'warehouse', 'warehouse_name', 'available_qty'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'email', 'created_at', 'orders_count', 'total_spent']
        read_only_fields = ['id', 'created_at']
    
    def get_orders_count(self, obj):
        return obj.orders.count()
    
    def get_total_spent(self, obj):
        return sum(
            payment.amount for payment in 
            Payment.objects.filter(order__customer=obj, status='CONFIRMED')
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'qty', 'unit_price', 'created_at',
            'product', 'product_name', 'product_sku', 'total_price'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        # Validar que haya stock disponible
        product = data['product']
        qty = data['qty']
        
        total_stock = sum(stock.available_qty for stock in product.stocks.all())
        if qty > total_stock:
            raise serializers.ValidationError(
                f"No hay suficiente stock. Disponible: {total_stock}, Solicitado: {qty}"
            )
        
        return data


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'created_at',
            'customer', 'customer_name', 'customer_email',
            'items', 'total_amount', 'total_items'
        ]
        read_only_fields = ['id', 'created_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['customer', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            # Si no se especifica unit_price, usar el precio del producto
            if 'unit_price' not in item_data:
                item_data['unit_price'] = item_data['product'].price
            
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class PaymentSerializer(serializers.ModelSerializer):
    order_customer_name = serializers.CharField(source='order.customer.full_name', read_only=True)
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'method', 'amount', 'status', 'created_at',
            'order', 'order_id', 'order_customer_name'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        # Validar que el monto coincida con el total de la orden
        order = data['order']
        amount = data['amount']
        
        if order.total_amount != amount:
            raise serializers.ValidationError(
                f"El monto del pago ({amount}) no coincide con el total de la orden ({order.total_amount})"
            )
        
        return data


# Serializers especiales para el método get_related
class RelatedFieldSerializer(serializers.Serializer):
    """Serializer dinámico para campos relacionados"""
    
    def __init__(self, model, fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        
        if fields:
            # Crear campos dinámicamente basados en los campos solicitados
            for field_name in fields:
                if hasattr(model, field_name):
                    field = model._meta.get_field(field_name)
                    if hasattr(field, 'related_model'):
                        # Campo relacional
                        self.fields[field_name] = serializers.StringRelatedField()
                    else:
                        # Campo normal
                        self.fields[field_name] = serializers.CharField()
        else:
            # Si no se especifican campos, usar todos los campos del modelo
            for field in model._meta.fields:
                if hasattr(field, 'related_model'):
                    self.fields[field.name] = serializers.StringRelatedField()
                else:
                    self.fields[field.name] = serializers.CharField() 
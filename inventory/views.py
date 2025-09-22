from django.db.models import Q, F, Count, Sum, Prefetch
from django.apps import apps
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
import logging

from .models import (
    Brand, Category, Product, Warehouse, 
    Stock, Customer, Order, OrderItem, Payment
)
from .serializers import (
    BrandSerializer, CategorySerializer, ProductSerializer, 
    WarehouseSerializer, StockSerializer, CustomerSerializer,
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer, 
    PaymentSerializer
)

logger = logging.getLogger(__name__)


class BaseRelatedViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que implementa el método get_related genérico
    para hacer JOINs parametrizables entre modelos
    """
    
    @action(detail=False, methods=['get'])
    def get_related(self, request):
        """
        Método genérico para obtener datos con JOINs parametrizables
        
        Parámetros de query:
        - join: relaciones a incluir (ej: brand,category,stocks__warehouse)
        - fields[modelo]: campos específicos por modelo (ej: fields[product]=name,sku)
        - filter[modelo]: filtros por modelo (ej: filter[brand]=name__icontains=Samsung)
        - ordering: ordenamiento (ej: ordering=name,-created_at)
        - distinct: eliminar duplicados (ej: distinct=true)
        - limit: limitar resultados (ej: limit=10)
        """
        
        try:
            # Obtener queryset base
            queryset = self.get_queryset()
            
            # Aplicar JOINs (select_related y prefetch_related)
            join_param = request.query_params.get('join', '')
            if join_param:
                queryset = self._apply_joins(queryset, join_param)
            
            # Aplicar filtros por modelo
            queryset = self._apply_filters(queryset, request.query_params)
            
            # Aplicar ordenamiento
            ordering_param = request.query_params.get('ordering', '')
            if ordering_param:
                ordering_fields = [field.strip() for field in ordering_param.split(',')]
                queryset = queryset.order_by(*ordering_fields)
            
            # Aplicar distinct si se solicita
            if request.query_params.get('distinct', '').lower() == 'true':
                queryset = queryset.distinct()
            
            # Aplicar limit si se solicita
            limit_param = request.query_params.get('limit', '')
            if limit_param and limit_param.isdigit():
                queryset = queryset[:int(limit_param)]
            
            # Log del SQL generado para debugging
            logger.debug(f"SQL Query: {str(queryset.query)}")
            
            # Serializar resultados
            serialized_data = self._serialize_related_data(
                queryset, request.query_params
            )
            
            return Response({
                'count': len(serialized_data),
                'results': serialized_data,
                'sql_query': str(queryset.query)  # Para comparación con función SQL
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _apply_joins(self, queryset, join_param):
        """Aplica JOINs usando select_related y prefetch_related"""
        joins = [join.strip() for join in join_param.split(',')]
        select_related_fields = []
        prefetch_related_fields = []
        
        for join in joins:
            if join:
                # Determinar si es una relación ForeignKey/OneToOne o ManyToMany/reverse FK
                if self._is_select_related_field(join):
                    select_related_fields.append(join)
                else:
                    prefetch_related_fields.append(join)
        
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)
        
        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)
        
        return queryset
    
    def _is_select_related_field(self, field_path):
        """Determina si un campo debe usar select_related o prefetch_related"""
        model = self.serializer_class.Meta.model
        parts = field_path.split('__')
        current_model = model
        
        for part in parts:
            try:
                field = current_model._meta.get_field(part)
                if hasattr(field, 'related_model'):
                    if field.many_to_many or field.one_to_many:
                        return False  # Usar prefetch_related
                    current_model = field.related_model
                else:
                    return True  # Campo normal, usar select_related
            except:
                return False
        
        return True
    
    def _apply_filters(self, queryset, query_params):
        """Aplica filtros por modelo usando el patrón filter[modelo]=campo=valor"""
        for param_name, param_value in query_params.items():
            if param_name.startswith('filter[') and param_name.endswith(']'):
                # Extraer modelo del parámetro filter[modelo]
                model_name = param_name[7:-1]  # Quitar 'filter[' y ']'
                
                # Parsear filtros: campo__lookup=valor,campo2=valor2
                filters = param_value.split(',')
                for filter_expr in filters:
                    if '=' in filter_expr:
                        field_lookup, value = filter_expr.split('=', 1)
                        
                        # Construir el filtro con prefijo del modelo si es necesario
                        if model_name.lower() != self.serializer_class.Meta.model.__name__.lower():
                            # Filtro para modelo relacionado
                            filter_key = f"{self._get_relation_path(model_name)}__{field_lookup}"
                        else:
                            # Filtro para modelo principal
                            filter_key = field_lookup
                        
                        # Convertir valores booleanos y numéricos
                        converted_value = self._convert_filter_value(value)
                        
                        # Aplicar filtro
                        filter_kwargs = {filter_key: converted_value}
                        queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
    def _get_relation_path(self, model_name):
        """Obtiene el path de relación para un modelo dado basado en el modelo actual"""
        current_model = self.serializer_class.Meta.model.__name__.lower()
        target_model = model_name.lower()
        
        # Mapeo dinámico basado en el modelo actual
        relation_paths = {
            # Desde Product
            'product': {
                'brand': 'brand',
                'category': 'category',
                'warehouse': 'stocks__warehouse',
                'stock': 'stocks',
                'customer': 'order_items__order__customer',
                'order': 'order_items__order',
                'orderitem': 'order_items',
                'payment': 'order_items__order__payment'
            },
            # Desde Brand
            'brand': {
                'product': 'products',
                'customer': 'products__order_items__order__customer',
                'order': 'products__order_items__order',
                'warehouse': 'products__stocks__warehouse'
            },
            # Desde Customer
            'customer': {
                'order': 'orders',
                'product': 'orders__items__product',
                'brand': 'orders__items__product__brand',
                'payment': 'orders__payment'
            },
            # Desde Order
            'order': {
                'customer': 'customer',
                'product': 'items__product',
                'brand': 'items__product__brand',
                'orderitem': 'items',
                'payment': 'payment'
            },
            # Desde Stock
            'stock': {
                'product': 'product',
                'warehouse': 'warehouse',
                'brand': 'product__brand',
                'category': 'product__category'
            },
            # Desde Warehouse
            'warehouse': {
                'product': 'stocks__product',
                'stock': 'stocks',
                'brand': 'stocks__product__brand'
            },
            # Desde Payment
            'payment': {
                'order': 'order',
                'customer': 'order__customer',
                'product': 'order__items__product'
            }
        }
        
        # Obtener el mapeo para el modelo actual
        current_paths = relation_paths.get(current_model, {})
        return current_paths.get(target_model, target_model)
    
    def _convert_filter_value(self, value):
        """Convierte valores de filtro a tipos apropiados"""
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.isdigit():
            return int(value)
        else:
            return value
    
    def _serialize_related_data(self, queryset, query_params):
        """Serializa los datos aplicando campos específicos por modelo"""
        # Obtener campos específicos por modelo
        model_fields = {}
        for param_name, param_value in query_params.items():
            if param_name.startswith('fields[') and param_name.endswith(']'):
                model_name = param_name[7:-1]
                fields = [field.strip() for field in param_value.split(',')]
                model_fields[model_name.lower()] = fields
        
        # Si no se especifican campos personalizados, usar serializer por defecto
        if not model_fields:
            serializer = self.get_serializer(queryset, many=True)
            return serializer.data
        
        # Serialización personalizada con campos específicos
        results = []
        for obj in queryset:
            obj_data = {}
            
            # Campos del modelo principal
            main_model_name = obj.__class__.__name__.lower()
            if main_model_name in model_fields:
                for field_name in model_fields[main_model_name]:
                    if hasattr(obj, field_name):
                        obj_data[field_name] = getattr(obj, field_name)
            else:
                # Usar serializer por defecto para modelo principal
                serializer = self.get_serializer(obj)
                obj_data.update(serializer.data)
            
            # Campos de modelos relacionados
            for model_name, fields in model_fields.items():
                if model_name != main_model_name:
                    related_data = self._get_related_fields(obj, model_name, fields)
                    if related_data:
                        obj_data[model_name] = related_data
            
            results.append(obj_data)
        
        return results
    
    def _get_related_fields(self, obj, model_name, fields):
        """Obtiene campos específicos de modelos relacionados"""
        try:
            # Mapeo de nombres de modelo a atributos de relación
            relation_map = {
                'brand': 'brand',
                'category': 'category',
                'warehouse': 'warehouse', 
                'product': 'product',
                'customer': 'customer',
                'order': 'order',
                'payment': 'payment',
                'stocks': 'stocks',
                'items': 'items'
            }
            
            relation_attr = relation_map.get(model_name)
            if not relation_attr or not hasattr(obj, relation_attr):
                return None
            
            related_obj = getattr(obj, relation_attr)
            
            # Manejar relaciones múltiples (Many-to-Many, reverse ForeignKey)
            if hasattr(related_obj, 'all'):
                related_data = []
                for item in related_obj.all():
                    item_data = {}
                    for field_name in fields:
                        if hasattr(item, field_name):
                            item_data[field_name] = getattr(item, field_name)
                    related_data.append(item_data)
                return related_data
            
            # Relación única (ForeignKey, OneToOne)
            else:
                if related_obj:
                    related_data = {}
                    for field_name in fields:
                        if hasattr(related_obj, field_name):
                            related_data[field_name] = getattr(related_obj, field_name)
                    return related_data
                
        except Exception as e:
            logger.warning(f"Error getting related fields for {model_name}: {e}")
            return None


class BrandViewSet(BaseRelatedViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtiene todos los productos de una marca"""
        brand = self.get_object()
        products = brand.products.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(BaseRelatedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtiene todos los productos de una categoría"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(BaseRelatedViewSet):
    queryset = Product.objects.select_related('brand', 'category').prefetch_related('stocks__warehouse')
    serializer_class = ProductSerializer
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Obtiene el stock de un producto en todas las bodegas"""
        product = self.get_object()
        stocks = product.stocks.select_related('warehouse')
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Obtiene productos con stock bajo"""
        threshold = int(request.query_params.get('threshold', 10))
        products = Product.objects.annotate(
            total_stock=Sum('stocks__qty')
        ).filter(
            total_stock__lt=threshold,
            is_active=True
        ).select_related('brand', 'category')
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class WarehouseViewSet(BaseRelatedViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Obtiene todo el stock de una bodega"""
        warehouse = self.get_object()
        stocks = warehouse.stocks.select_related('product__brand', 'product__category')
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)


class StockViewSet(BaseRelatedViewSet):
    queryset = Stock.objects.select_related('product__brand', 'product__category', 'warehouse')
    serializer_class = StockSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Obtiene stock disponible (no reservado)"""
        stocks = self.get_queryset().filter(qty__gt=F('reserved'))
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class CustomerViewSet(BaseRelatedViewSet):
    queryset = Customer.objects.prefetch_related('orders__items__product')
    serializer_class = CustomerSerializer
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Obtiene todas las órdenes de un cliente"""
        customer = self.get_object()
        orders = customer.orders.prefetch_related('items__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderViewSet(BaseRelatedViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related(
        'items__product__brand',
        'items__product__category',
        'payment'
    )
    serializer_class = OrderSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma una orden y reserva el stock"""
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden confirmar órdenes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar y reservar stock
        try:
            for item in order.items.all():
                # Buscar stock disponible
                available_stocks = Stock.objects.filter(
                    product=item.product,
                    qty__gt=F('reserved')
                ).order_by('-qty')
                
                remaining_qty = item.qty
                for stock in available_stocks:
                    if remaining_qty <= 0:
                        break
                    
                    available = stock.qty - stock.reserved
                    to_reserve = min(available, remaining_qty)
                    
                    stock.reserved += to_reserve
                    stock.save()
                    
                    remaining_qty -= to_reserve
                
                if remaining_qty > 0:
                    raise ValidationError(
                        f"Stock insuficiente para {item.product.name}. Faltantes: {remaining_qty}"
                    )
            
            order.status = 'CONFIRMED'
            order.save()
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderItemViewSet(BaseRelatedViewSet):
    queryset = OrderItem.objects.select_related('order__customer', 'product__brand', 'product__category')
    serializer_class = OrderItemSerializer


class PaymentViewSet(BaseRelatedViewSet):
    queryset = Payment.objects.select_related('order__customer')
    serializer_class = PaymentSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma un pago"""
        payment = self.get_object()
        
        if payment.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden confirmar pagos pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'CONFIRMED'
        payment.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data) 
from django.contrib import admin
from .models import (
    Brand, Category, Product, Warehouse, 
    Stock, Customer, Order, OrderItem, Payment
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'brand', 'category', 'price', 'is_active']
    list_filter = ['brand', 'category', 'is_active', 'created_at']
    search_fields = ['name', 'sku']
    readonly_fields = ['id', 'created_at']
    list_select_related = ['brand', 'category']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'city']
    readonly_fields = ['id', 'created_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'qty', 'reserved', 'available_qty', 'updated_at']
    list_filter = ['warehouse', 'updated_at']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'available_qty']
    list_select_related = ['product', 'warehouse']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'created_at']
    search_fields = ['full_name', 'email']
    readonly_fields = ['id', 'created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['id', 'created_at', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total_items', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__full_name', 'customer__email']
    readonly_fields = ['id', 'created_at', 'total_items', 'total_amount']
    list_select_related = ['customer']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'qty', 'unit_price', 'total_price']
    list_filter = ['created_at']
    search_fields = ['product__name', 'product__sku', 'order__customer__full_name']
    readonly_fields = ['id', 'created_at', 'total_price']
    list_select_related = ['product', 'order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'amount', 'status', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['order__customer__full_name']
    readonly_fields = ['id', 'created_at']
    list_select_related = ['order'] 
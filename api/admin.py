from django.contrib import admin
from .models import Restaurant, Category, Product, ProductVariant, Order, OrderItem

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    list_filter = ('created_at',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'resturant')
    search_fields = ('name',)
    list_filter = ('category', 'resturant')

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'price', 'gst_percent')
    search_fields = ('name', 'product__name')
    list_filter = ('product',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date', 'total_price', 'status', 'mode')
    search_fields = ('order_number',)
    list_filter = ('status', 'mode', 'order_date')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price', 'total_price', 'gst')
    search_fields = ('order__order_number', 'product_variant__name')
    list_filter = ('order', 'product_variant')

# Register your models here
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

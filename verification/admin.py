from django.contrib import admin
from .models import Product, VerificationResult

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'name', 'brand', 'image')  # Fields to display in the admin list view
    search_fields = ('barcode', 'name', 'brand')  # Fields to search in the admin interface
    list_filter = ('brand',)  # Filters for the admin list view

@admin.register(VerificationResult)
class VerificationResultAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'image', 'is_authentic', 'created_at')  # Fields to display in the admin list view
    search_fields = ('barcode', 'details')  # Fields to search in the admin interface
    list_filter = ('is_authentic', 'created_at')  # Filters for the admin list view
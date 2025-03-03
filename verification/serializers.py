from rest_framework import serializers
from .models import Product, VerificationResult

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class VerificationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationResult
        fields = '__all__'
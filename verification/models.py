from django.db import models

class Product(models.Model):
    barcode = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # Updated to ImageField
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class VerificationResult(models.Model):
    barcode = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='verification_images/', blank=True, null=True)  # Updated to ImageField
    is_authentic = models.BooleanField(default=False)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification Result for {self.barcode or 'Image'}"
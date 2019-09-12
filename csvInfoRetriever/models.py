from django.db import models
from django.utils import timezone


class Product(models.Model):
    sku = models.CharField(max_length=128)
    stock = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    last_stock_reported_centry = models.IntegerField(null=True)
    last_price_reported_centry = models.FloatField(null=True)
    id_product_centry = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField('date published')
    updated_at = models.DateTimeField('date updated')

    def save(self, *args, **kwargs):
        # agrega timestamps al producto
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)
from django.db import models

class SavedItem(models.Model):
    ebay_id = models.CharField(max_length=255)
    date = models.DateField()
    name = models.CharField(max_length=255)
    image_url = models.URLField(default='https://example.com/default-image.jpg')
    ebay_url = models.URLField(default='https://www.ebay.com/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    time_left = models.CharField(max_length=255, default='')
    ungraded_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grade7_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grade8_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grade9_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grade95_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grade10_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

    def __str__(self):
        return self.name
    
class EbayAPIKey(models.Model):
    api_key = models.CharField(max_length=3000)

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure only one instance exists
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = 'eBay API Key'
        verbose_name_plural = 'eBay API Keys'

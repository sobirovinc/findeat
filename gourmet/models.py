from django.db import models

# Create your models here.


class Like(models.Model):
    visitor_id = models.CharField(max_length=255)
    shop_id = models.CharField(max_length=100)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor_id', 'shop_id')


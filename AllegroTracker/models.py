from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    minutes_refresh_rate = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    target_price = models.FloatField() 

    def __str__(self):
        return str(self.id) + " - " + self.name

    class Meta:
        ordering = ['-date_added']


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    currency = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product) + " - " + str(self.price) + " " + self.currency

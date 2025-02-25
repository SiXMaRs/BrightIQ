from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.menu.name} x{self.quantity}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'wait'),
        ('completed', 'success'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.IntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='order_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')  # เพิ่มสถานะ

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


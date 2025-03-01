from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Topping(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    toppings = models.ManyToManyField(Topping, blank=True)
    total_price = models.IntegerField(default=0)  # ✅ เพิ่มฟิลด์นี้

    def save(self, *args, **kwargs):
        is_new = self.id is None  # ✅ เช็คว่าเป็น object ใหม่หรือไม่
        
        super().save(*args, **kwargs)  # ✅ บันทึกก่อนครั้งแรกถ้าเป็น object ใหม่

        if is_new:
            # ✅ คำนวณราคาของ toppings หลังจาก instance ถูกบันทึก
            topping_price = sum(topping.price for topping in self.toppings.all())
            self.total_price = (self.menu.price + topping_price) * self.quantity
            super().save(*args, **kwargs)
 
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    toppings = models.ManyToManyField(Topping, blank=True)  # เพิ่มท็อปปิ้งในคำสั่งซื้อ

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


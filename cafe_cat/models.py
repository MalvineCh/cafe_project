from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    summary = models.TextField()
    is_featured = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    image = models.ImageField(upload_to='menu_item_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.on_sale:
            # Применяем скидку, если блюдо находится на распродаже
            # Здесь можно определить, какую скидку вы хотите применить
            # Например, снижение цены на 20%
            self.sale_price = self.price * (1 - self.discount / 100)
        else:
            # Если блюдо не находится на распродаже, скидка не применяется
            self.discount = Decimal('0')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Cart(models.Model):
    """ Модель корзины, ассоциирована с пользователем и содержит элементы меню. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    items = models.ManyToManyField(MenuItem, through='CartItem')
    session_key = models.CharField(max_length=100, null=True, blank=True)  # Добавлено поле session_key

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class CartItem(models.Model):
    """ Модель элемента в корзине, связывает корзину, элемент меню и количество. """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


from django.utils import timezone

from django.db import models

from django.db import models

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(max_length=100, default='')
    phone_number = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, default='Pending')
    loyalty_points_used = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    """ Модель элемента в заказе, связывает заказ, элемент меню и количество. """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

class LoyaltyCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=100)  # Устанавливаем значение по умолчанию

    def add_points(self, amount):
        self.points += amount
        self.save()

    def deduct_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            self.save()
            return True
        return False
    def __str__(self):
        return f"Loyalty card for {self.user.username}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    loyalty_card = models.OneToOneField(LoyaltyCard, on_delete=models.CASCADE, null=True, blank=True)  # Поле loyalty_card
    def __str__(self):
        return self.user.username

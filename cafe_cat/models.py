from django.db import models
from django.conf import settings
from decimal import Decimal
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    summary = models.TextField()
    is_featured = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(MenuItem, through='CartItem')

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

class CartItem(models.Model):
    """ Модель элемента в корзине, связывает корзину, элемент меню и количество. """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

class Order(models.Model):
    """ Модель заказа, содержит элементы, заказанные пользователем, и метку времени создания. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True)
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

class OrderItem(models.Model):
    """ Модель элемента в заказе, связывает заказ, элемент меню и количество. """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

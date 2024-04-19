from django.db import models
from django.conf import settings

class MenuItem(models.Model):
    """ Модель элемента меню в ресторане, содержит информацию о блюде. """
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    summary = models.CharField(max_length=100, unique=True)

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

from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from .models import MenuItem, Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)
    list_display = ('id', 'date_created', 'user')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items']
    inlines = [CartItemInline]

    def get_items(self, obj):
        return ", ".join([str(item) for item in obj.items.all()])
    get_items.short_description = 'Позиции в корзине'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'cart']
    actions = ['create_order_from_cartitem']

    @transaction.atomic
    def create_order_from_cartitem(self, request, queryset):
        for cart_item in queryset:
            order = Order.objects.create(user=cart_item.cart.user)
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                quantity=cart_item.quantity
            )
            cart_item.cart.items.remove(cart_item.item)
            messages.success(request, f"Order #{order.id} was successfully created from cart item.")

    create_order_from_cartitem.short_description = "Create Order from Selected Cart Items"

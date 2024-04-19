from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import MenuItem, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db import transaction

def home(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'cafe_cat/index.html', {'menu_items': menu_items})

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user, defaults={'user': request.user})
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('home')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user, defaults={'user': request.user})
    return render(request, 'cafe_cat/cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    order = Order.objects.create(user=request.user)
    for cart_item in cart.items.all():
        OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)
        cart.items.remove(cart_item.item)
    return redirect('order_success', order_id=order.id)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cafe_cat/order_success.html', {'order': order})

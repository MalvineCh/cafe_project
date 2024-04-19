from datetime import timezone

from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuItem, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required

def home(request):
    # Покажем избранные товары на главной странице
    featured_items = MenuItem.objects.filter(is_featured=True)
    return render(request, 'cafe_cat/index.html', {'featured_items': featured_items})

def add_to_cart(request, item_id=None):
    # Это простое добавление в корзину. Не забудьте реализовать логику для управления сессиями или идентификаторами покупателей
    if item_id:
        item = get_object_or_404(MenuItem, pk=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user, defaults={'created_at': timezone.now()})
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, defaults={'quantity': 1})
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('cafe_cat:view_cart')
    return redirect('cafe_cat:menu')

def view_cart(request):
    # Позволяет просмотреть содержимое корзины
    cart = None
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            pass
    return render(request, 'cafe_cat/view_cart.html', {'cart': cart})
@login_required
def checkout(request):
    # Логика оформления заказа
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        order = Order.objects.create(user=request.user)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, item=item.item, quantity=item.quantity)
        cart.delete()
        return redirect('cafe_cat:order_success', order_id=order.id)
    return render(request, 'cafe_cat/checkout.html')

def order_success(request, order_id):
    # Показывает страницу успешного создания заказа
    return render(request, 'cafe_cat/order_success.html', {'order_id': order_id})

def menu(request):
    # Показать список меню
    menu_items = MenuItem.objects.all()
    return render(request, 'cafe_cat/menu.html', {'menu_items': menu_items})

def account(request):
    # Логика для представления страницы аккаунта
    return render(request, 'cafe_cat/account.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('cafe_cat:account')
    else:
        form = AuthenticationForm()
    return render(request, 'cafe_cat/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('cafe_cat:account')
    else:
        form = UserCreationForm()
    return render(request, 'cafe_cat/register.html', {'form': form})

def account(request):
    # Логика для страницы аккаунта
    return render(request, 'cafe_cat/account.html')

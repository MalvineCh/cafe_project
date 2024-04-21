from datetime import timezone, datetime

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

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

from django.shortcuts import render
from .models import MenuItem

def menu(request):
    items = MenuItem.objects.all()  # Получение всех элементов меню
    return render(request, 'cafe_cat/menu.html', {
        'items': items
    })
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
                auth_login(request, user)
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

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('cafe_cat:account')
    else:
        form = AuthenticationForm()
    return render(request, 'cafe_cat/login.html', {'form': form})

from django.shortcuts import redirect

def add_to_cart(request, item_id=None):
    if item_id:
        item = get_object_or_404(MenuItem, pk=item_id)
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'created_at': datetime.now()}
        )
        quantity = int(request.POST.get('quantity', 1))  # Получаем количество из формы
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=item,
            defaults={'quantity': quantity}  # Устанавливаем указанное количество товара
        )
        if not created:
            cart_item.quantity += quantity  # Увеличиваем количество на указанное значение
            cart_item.save()
        return redirect('cafe_cat:view_cart')
    return redirect('cafe_cat:menu')

from django.shortcuts import render
from .models import CartItem

# cafe_cat/views.py

# cafe_cat/views.py

def view_cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = 0
    for cart_item in cart_items:
        cart_item.item_total = cart_item.item.price * cart_item.quantity
        total_price += cart_item.item_total
    return render(request, 'cafe_cat/view_cart.html', {'cart_items': cart_items, 'total_price': total_price})

def remove_from_cart(request, cart_item_id):
    # Получаем объект товара в корзине по его идентификатору
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    # Удаляем товар из корзины
    cart_item.delete()

    # Перенаправляем пользователя на страницу просмотра корзины
    return redirect('cafe_cat:view_cart')

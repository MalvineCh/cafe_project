from datetime import timezone, datetime

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UpdateQuantityForm, OrderForm
from .models import MenuItem, Cart, CartItem, Order, OrderItem
from django.contrib import messages
def home(request):
    # Покажем избранные товары на главной странице
    featured_items = MenuItem.objects.filter(is_featured=True)
    return render(request, 'cafe_cat/index.html', {'featured_items': featured_items})
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            delivery_address = form.cleaned_data['delivery_address']
            contact_number = form.cleaned_data['contact_number']
            menu_items = form.cleaned_data['menu_items']

            # Создаем новый заказ
            order = Order.objects.create(
                user=request.user,
                delivery_address=delivery_address,
                contact_number=contact_number
            )

            # Добавляем выбранные блюда в заказ
            for item_id in menu_items:
                menu_item = MenuItem.objects.get(pk=item_id)
                OrderItem.objects.create(order=order, item=menu_item)

            # Очищаем корзину пользователя
            CartItem.objects.filter(cart__user=request.user).delete()

            messages.success(request, 'Заказ успешно оформлен!')
            return redirect('cafe_cat:order_success', order_id=order.id)
    else:
        # Если метод запроса GET, создаем пустую форму заказа
        form = OrderForm()

    # Получаем все товары из меню для отображения в форме
    menu_items = MenuItem.objects.all()

    return render(request, 'cafe_cat/checkout.html', {'form': form, 'menu_items': menu_items})

def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Обработка формы, сохранение заказа и т.д.
            return redirect('cafe_cat:order_success')  # Перенаправление на страницу успешного заказа
    else:
        form = OrderForm()
    return render(request, 'cafe_cat/place_order.html', {'form': form})

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

from .forms import UpdateQuantityForm

def view_cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items)
    total_quantity = sum(cart_item.quantity for cart_item in cart_items)
    update_forms = {str(cart_item.id): UpdateQuantityForm(instance=cart_item) for cart_item in cart_items}
    return render(request, 'cafe_cat/view_cart.html', {'cart_items': cart_items, 'total_price': total_price,
                                                       'total_quantity': total_quantity, 'update_forms': update_forms})
def remove_selected(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        CartItem.objects.filter(id__in=selected_items).delete()
        return redirect('cafe_cat:view_cart')
    return JsonResponse({'status': 'error'})
def place_order_selected(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        items_to_order = CartItem.objects.filter(id__in=selected_items)
        order = Order.objects.create(user=request.user)
        for item in items_to_order:
            OrderItem.objects.create(order=order, item=item.item, quantity=item.quantity)
        items_to_order.delete()  # Remove items from cart after placing order
    return redirect('cafe_cat:view_cart')

def update_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if request.method == 'POST':
        form = UpdateQuantityForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
    return redirect('cafe_cat:view_cart')

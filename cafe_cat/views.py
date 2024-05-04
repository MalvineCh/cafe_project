from datetime import timezone, datetime

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UpdateQuantityForm, OrderForm, ProfileUpdateForm
from .models import MenuItem, Cart, CartItem, Order, OrderItem, Profile
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
@login_required
def account(request):
    # Получение пользователя из запроса
    user = request.user

    # Если метод запроса POST, значит пользователь отправил форму для обновления дня рождения
    if request.method == 'POST':
        # Создание формы для обновления профиля с переданными данными из запроса
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        # Проверка валидности формы
        if form.is_valid():
            # Сохранение данных профиля
            form.save()
            # Перенаправление пользователя на страницу аккаунта с обновленными данными
            return redirect('cafe_cat:account')
    else:
        # Если метод запроса GET, создаем форму для обновления профиля с текущими данными пользователя
        form = ProfileUpdateForm(instance=request.user.profile)

    # Возвращаем HTML-страницу с контекстом, включающим пользователя и форму для обновления профиля
    return render(request, 'cafe_cat/account.html', {'user': user, 'form': form})

def profile_update(request):
    user = request.user
    try:
        profile = user.profile  # Попытка получить профиль пользователя
    except Profile.DoesNotExist:
        profile = Profile(user=user)  # Если профиль не существует, создаем новый
        profile.save()
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('cafe_cat:account')  # Перенаправляем пользователя после обновления профиля
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'cafe_cat/profile_update.html', {'form': form})
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
            login(request, user)  # Убедитесь, что здесь вызывается login только с объектом запроса
            return redirect('cafe_cat')
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

from django.shortcuts import redirect, get_object_or_404

from django.shortcuts import redirect, get_object_or_404
from .models import MenuItem, Cart, CartItem

from django.contrib.sessions.models import Session

def add_to_cart(request, item_id=None):
    if item_id:
        item = get_object_or_404(MenuItem, pk=item_id)

        if request.user.is_authenticated:
            user = request.user
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            # Создаем сеанс, если он еще не существует
            if not request.session.session_key:
                request.session.create()
            session = Session.objects.get(session_key=request.session.session_key)
            cart, created = Cart.objects.get_or_create(session=session)

        quantity = int(request.POST.get('quantity', 1))
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=item,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if request.user.is_authenticated:
            return redirect('cafe_cat:menu')
    return redirect('cafe_cat:menu')


from django.shortcuts import render
from .models import CartItem

from .forms import UpdateQuantityForm

def view_cart(request):
    # Получаем текущего пользователя
    user = request.user

    # Проверяем, аутентифицирован ли пользователь
    if user.is_authenticated:
        # Получаем или создаем корзину пользователя
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        # Если пользователь не аутентифицирован, создаем корзину без привязки к пользователю
        cart, created = Cart.objects.get_or_create()

    # Получаем все элементы корзины для текущего пользователя
    cart_items = CartItem.objects.filter(cart=cart)

    # Вычисляем общую стоимость и количество элементов в корзине
    total_price = 0
    for cart_item in cart_items:
        if cart_item.item.on_sale:
            total_price += cart_item.item.sale_price * cart_item.quantity
        else:
            total_price += cart_item.item.price * cart_item.quantity
    total_quantity = sum(cart_item.quantity for cart_item in cart_items)


    for cart_item in cart_items:
        if cart_item.item.on_sale:
            cart_item.total_item = cart_item.item.sale_price * cart_item.quantity
        else:
            cart_item.total_item = cart_item.item.price * cart_item.quantity
    # Создаем словарь форм обновления количества для каждого элемента корзины
    update_forms = {str(cart_item.id): UpdateQuantityForm(instance=cart_item) for cart_item in cart_items}

    # Передаем данные в шаблон для отображения
    return render(request, 'cafe_cat/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'update_forms': update_forms
    })

def remove_selected(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        CartItem.objects.filter(id__in=selected_items).delete()
        return redirect('cafe_cat:view_cart')
    return JsonResponse({'status': 'error'})

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from .forms import OrderForm
from decimal import Decimal
from django.shortcuts import render, redirect

@login_required
def place_order_selected(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    selected_item_ids = request.POST.getlist('selected_items')

    selected_cart_items = CartItem.objects.filter(id__in=selected_item_ids, cart=cart)
    total_price = Decimal('0.00')
    for cart_item in selected_cart_items:
        if cart_item.item.on_sale:
            total_price += cart_item.item.sale_price * cart_item.quantity
        else:
            total_price += cart_item.item.price * cart_item.quantity

    if request.method == 'POST':
        print(CartItem.objects.filter(id__in=selected_item_ids, cart=cart))
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.save()
            for cart_item in selected_cart_items:
                OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)
            selected_cart_items.delete()
            return redirect('cafe_cat:user_orders')
    else:
        form = OrderForm(initial={'menu_items': selected_cart_items})
    if not selected_item_ids:
        return redirect('cafe_cat:view_cart')
    return render(request, 'cafe_cat/place_order_selected.html', {
        'form': form,
        'selected_cart_items': selected_cart_items,
        'total_price': total_price
    })




def update_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if request.method == 'POST':
        form = UpdateQuantityForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
    return redirect('cafe_cat:view_cart')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    return render(request, 'cafe_cat/user_orders.html', {'orders': orders})
@login_required
def delete_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        if order.user == request.user:
            order.delete()
            return redirect('cafe_cat:user_orders')
        else:
            return HttpResponse("You are not authorized to delete this order.")
    except Order.DoesNotExist:
        return HttpResponse("Order does not exist.")

from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'cafe_cat/order_detail.html', {'order': order, 'order_items': order_items})

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponse
from .forms import ProfileUpdateForm, UpdateQuantityForm
from .models import Profile, LoyaltyCard

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
@login_required(login_url='/cafe_cat/login/')
def account(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Проверяем, есть ли уже карта лояльности, связанная с этим профилем
    loyalty_card = LoyaltyCard.objects.filter(user=user).first()
    if not loyalty_card:
        # Если карты лояльности нет, создаем новую и связываем ее с профилем
        loyalty_card = LoyaltyCard.objects.create(user=user)
        profile.loyalty_card = loyalty_card
        profile.save()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('cafe_cat:account')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'cafe_cat/account.html', {'user': user, 'form': form, 'loyalty_card_points': loyalty_card.points})


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
            # Создание профиля и карты лояльности для нового пользователя
            profile = Profile.objects.create(user=user)
            loyalty_card = LoyaltyCard.objects.create(user=user)
            profile.loyalty_card = loyalty_card
            profile.save()
            auth_login(request, user)  # Убедитесь, что здесь вызывается login с request и user
            return redirect('cafe_cat:account')
    else:
        form = UserCreationForm()
    return render(request, 'cafe_cat/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('cafe_cat:account')
    else:
        form = AuthenticationForm()
    return render(request, 'cafe_cat/login.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.exceptions import MultipleObjectsReturned
from .models import Cart, MenuItem, CartItem

def add_to_cart(request, item_id):
    print("Adding item to cart...")

    # Получаем элемент меню, который пользователь хочет добавить в корзину
    menu_item = get_object_or_404(MenuItem, pk=item_id)
    print("Menu item:", menu_item)

    # Попытка получить корзину пользователя
    user_cart = None
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        carts = Cart.objects.filter(session_key=session_key)
        if carts.exists():
            user_cart = carts.first()
        else:
            user_cart = Cart.objects.create(session_key=session_key)

    # Пытаемся получить элемент корзины для данного блюда и данной корзины
    try:
        cart_item = CartItem.objects.get(cart=user_cart, item=menu_item)
        cart_item.quantity += 1  # Увеличиваем количество товара на 1
        cart_item.save()
        print("Existing cart item:", cart_item)
    except CartItem.DoesNotExist:
        # Если элемента корзины нет, создаем новый
        cart_item = CartItem.objects.create(cart=user_cart, item=menu_item, quantity=1)
        print("New cart item:", cart_item)

    print("Item added to cart successfully.")

    return redirect('cafe_cat:menu')

def view_cart(request):
    # Попытка получить корзину пользователя
    user_cart = None
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        carts = Cart.objects.filter(session_key=session_key)
        if carts.exists():
            user_cart = carts.first()
        else:
            user_cart = Cart.objects.create(session_key=session_key)

    # Получаем все элементы корзины для данной корзины
    cart_items = CartItem.objects.filter(cart=user_cart)

    # Вычисляем общую стоимость и количество элементов в корзине
    total_price = sum(cart_item.item.sale_price * cart_item.quantity if cart_item.item.on_sale else cart_item.item.price * cart_item.quantity for cart_item in cart_items)
    total_quantity = sum(cart_item.quantity for cart_item in cart_items)

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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem
from .forms import OrderForm

def place_order_selected(request):
    user = request.user if request.user.is_authenticated else None

    # Получение или создание корзины для пользователя или по сессии
    if user:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, defaults={'user': None})

    # При методе POST находим выбранные товары
    selected_item_ids = request.POST.getlist('selected_items') if request.method == 'POST' else None

    # Фильтрация элементов корзины по выбранным id
    selected_cart_items = CartItem.objects.filter(id__in=selected_item_ids, cart=cart) if selected_item_ids else None
    if not selected_cart_items:
        # Если нет выбранных товаров, возвращаем пользователя в корзину
        return redirect('cafe_cat:view_cart')

    total_price = Decimal('0.00')
    for cart_item in selected_cart_items:
        # Расчет общей суммы заказа с учетом возможных скидок
        item_price = cart_item.item.sale_price if cart_item.item.on_sale else cart_item.item.price
        total_price += item_price * cart_item.quantity

    if request.method == 'POST' and selected_item_ids:
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if user:
                order.user = user

            if user and 'use_points' in request.POST and request.POST['use_points'] == 'on':
                if user.profile.loyalty_card:
                    loyalty_card = user.profile.loyalty_card
                    # Если используются баллы, и их достаточно, вычитаем из общей суммы
                    if loyalty_card.points >= 0:
                        points_to_deduct = min(loyalty_card.points, total_price)
                        total_price -= points_to_deduct
                        loyalty_card.points -= points_to_deduct
                        loyalty_card.points += (total_price * Decimal(0.05))
                        loyalty_card.save()
                        order.loyalty_points_used = True
                    else:
                        messages.error(request, "You do not have enough loyalty points to make this purchase.")
                        return redirect('cafe_cat:place_order_selected')
                else:
                    messages.error(request, "No loyalty card found.")
                    return redirect('cafe_cat:place_order_selected')

            order.total_price = total_price
            order.save()
            # Создание объектов OrderItem и удаление элементов из корзины
            for cart_item in selected_cart_items:
                OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)
            selected_cart_items.delete()
            # Перенаправление на страницу заказов пользователя или подтверждения заказа
            return redirect('cafe_cat:user_orders' if user else 'cafe_cat:order_success', order_id=order.id)
        elif not form.is_valid():
            return render(request, 'cafe_cat/place_order_selected.html', {
                'form': form,
                'selected_cart_items': selected_cart_items,
                'total_price': total_price,
                'error_message': "Форма невалидна. Исправьте ошибки.",
                'loyalty_points': user.profile.loyalty_card.points if user and user.profile.loyalty_card else 0
            })
    else:
        form = OrderForm()

    if not selected_item_ids:
        # Если нет выбранных товаров, возвращаем пользователя в корзину
        return redirect('cafe_cat:view_cart')

    return render(request, 'cafe_cat/place_order_selected.html', {
        'form': form,
        'selected_cart_items': selected_cart_items,
        'total_price': total_price,
        'loyalty_points': user.profile.loyalty_card.points if user and user.profile.loyalty_card else 0
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

@login_required(login_url='/cafe_cat/login/')
def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    return render(request, 'cafe_cat/user_orders.html', {'orders': orders})
@login_required(login_url='/cafe_cat/login/')
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

from decimal import Decimal

@login_required(login_url='/cafe_cat/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.filter(order=order)
    total_price = Decimal(0.00)
    for order_item in order_items:
        # Расчет общей суммы заказа с учетом возможных скидок
        item_price = order_item.item.sale_price if order_item.item.on_sale else order_item.item.price
        total_price += item_price * order_item.quantity
    available_points = order.user.profile.loyalty_card.points if order.user.profile.loyalty_card else 0
    if request.method == 'POST':
        return redirect('cafe_cat:order_detail', order_id=order_id)
    return render(request, 'cafe_cat/order_detail.html', {'order': order, 'order_items': order_items,
                                                          'total_price_with_points': order.total_price,
                                                          'available_points': available_points,
                                                          'total_price': total_price})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def apply_loyalty_points(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        use_loyalty_points = request.POST.get('use_loyalty_points')  # Получаем значение флажка использования баллов лояльности
        if use_loyalty_points:
            # Проверяем, есть ли достаточное количество баллов у пользователя
            if order.user.profile.loyalty_card.points >= 320:
                # Вычитаем баллы лояльности из карты пользователя и обновляем сумму заказа
                order.user.profile.loyalty_card.points -= 320
                order.save()
                messages.success(request, 'Баллы лояльности успешно списаны.')
            else:
                messages.error(request, 'Недостаточно баллов лояльности для совершения заказа.')
        else:
            messages.info(request, 'Баллы лояльности не были использованы.')

    return redirect('cafe_cat:order_detail', order_id=order_id)

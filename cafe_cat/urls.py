# cafe_cat/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'cafe_cat'

urlpatterns = [
    path('', views.home, name='index'),
    path('menu/', views.menu, name='menu'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('account/', views.account, name='account'),  # URL-адрес для страницы аккаунта
    path('register/', views.register, name='register'),  # URL-адрес для страницы регистрации
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('remove_selected/', views.remove_selected, name='remove_selected'),
    path('place_order_selected/', views.place_order_selected, name='place_order_selected'),
    path('update_quantity/<int:cart_item_id>/', views.update_quantity, name='update_quantity'),
    path('place_order/', views.place_order, name='place_order'),
]

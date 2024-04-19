# cafe/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cafe_cat/', include('cafe_cat.urls', namespace='cafe_cat')),  # Включение URL-адресов приложения cafe_cat с префиксом
    # Другие ваши URL-адреса
]

# Используйте static() чтобы добавить соотношения для статических файлов
# Только на период разработки
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django import forms
from .models import CartItem, Order


class UpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
        }

from django import forms
from .models import CartItem

class OrderForm(forms.ModelForm):
    delivery_address = forms.CharField(label='Адрес доставки', max_length=100)
    contact_number = forms.CharField(label='Контактный номер', max_length=20)
    menu_items = forms.ModelMultipleChoiceField(queryset=CartItem.objects.none(), widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Order
        fields = ['delivery_address', 'contact_number', 'menu_items']

from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birthday']  # Здесь указываются поля, которые могут быть обновлены в профиле пользователя

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # Добавление атрибутов для HTML-элементов формы, например, классов CSS или атрибутов placeholder
        self.fields['birthday'].widget.attrs['class'] = 'form-control'
        self.fields['birthday'].widget.attrs['placeholder'] = 'Введите день рождения'

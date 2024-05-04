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
    address = forms.CharField(label='Delivery address', max_length=100, required=True)
    phone_number = forms.CharField(label='Phone number', max_length=20, required=True)
    full_name = forms.CharField(label='Full name', max_length=100, required=True)

    class Meta:
        model = Order
        fields = ['address', 'phone_number', 'full_name']

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

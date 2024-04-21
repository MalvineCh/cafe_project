from django import forms
from .models import CartItem

class UpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
        }

from django import forms
from .models import CartItem

class OrderForm(forms.Form):
    delivery_address = forms.CharField(label='Адрес доставки', max_length=100)
    contact_number = forms.CharField(label='Контактный номер', max_length=20)
    menu_items = forms.ModelMultipleChoiceField(queryset=CartItem.objects.all(), widget=forms.CheckboxSelectMultiple, required=True)


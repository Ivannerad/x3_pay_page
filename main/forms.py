from django import forms
from .models import PaymentInfo

class PaymentInfoForm(forms.ModelForm):
    
    class Meta:
        model = PaymentInfo
        fields = ('phone', 'money',)
        widgets = { 'phone': forms.TextInput(attrs={'class': "payment__input", 'type': "text", 'name': "phone-field", 'placeholder': "+7 (XXX)-XXX-XX-XX", 'id': "phone-field"}), 'money': forms.TextInput(attrs={'class': "payment__input", 'type': "number", 'name': "singly-field", 'placeholder': "Сумма пополнения", 'id': "singly-field"})}
    
    
    

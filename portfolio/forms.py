from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

from .models import Customer, Stock, Investment

class DateInput(forms.DateInput):
    input_type = "date"

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput,required=True)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput,required=True)
    email = forms.EmailField(label='Email', max_length=254, help_text='Required. Enter a valid email address.',required=True)
    first_name = forms.CharField(max_length=50,required=True)
    last_name = forms.CharField(max_length=50,required=True)
    group = forms.ModelChoiceField(queryset=Group.objects.all(),
                                   required=True)
    class Meta:
        model = User
        fields = ('username','email', 'first_name','last_name','password1','password2','group')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
           raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('cust_number', 'name', 'address', 'city', 'state', 'zipcode', 'email', 'cell_phone',)

class StockForm(forms.ModelForm):
   class Meta:
       model = Stock
       fields = ('customer', 'symbol', 'name', 'shares', 'purchase_price', 'purchase_date',)

   def __init__(self, *args, **kwargs):
       super(StockForm, self).__init__(*args, **kwargs)
       self.fields['purchase_date'].widget = DateInput()

class InvestmentForm(forms.ModelForm):
   class Meta:
       model = Investment
       fields = ('customer', 'category', 'description', 'acquired_value', 'acquired_date', 'recent_value','recent_date',)

   def __init__(self, *args, **kwargs):
           super(InvestmentForm, self).__init__(*args, **kwargs)
           self.fields['acquired_date'].widget = DateInput()
           self.fields['recent_date'].widget = DateInput()

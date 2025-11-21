from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Vehicle, Rental, Expense, UserProfile

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'registration_number', 'color', 'image']

class RentalForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        required=False,
        empty_label="Select Partner (Optional)",
        help_text="Select the partner responsible for this rental"
    )
    
    class Meta:
        model = Rental
        fields = [
            'user', 'date_out', 'time_out', 'date_in', 'time_in',
            'customer_name', 'contact_no', 'customer_id', 'care_of', 'destination',
            'days_of_rent', 'rent_per_day', 'advance_amount',
            'starting_km', 'ending_km', 'total_amount_received'
        ]
        widgets = {
            'date_out': forms.DateInput(attrs={'type': 'date'}),
            'date_in': forms.DateInput(attrs={'type': 'date'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
        }

class ExpenseForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        required=False,
        empty_label="Select Partner (Optional)",
        help_text="Select the partner responsible for this expense"
    )
    
    class Meta:
        model = Expense
        fields = ['user', 'date', 'particulars', 'place', 'care_of', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address")
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter first name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Enter last name")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password validators
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = "Enter the same password as before, for verification."
    
    def clean_password1(self):
        # Skip password validation
        password1 = self.cleaned_data.get('password1')
        return password1
    
    def clean_password2(self):
        # Only check if passwords match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = False
        user.is_superuser = False
            
        if commit:
            user.save()
            # Create profile as partner
            UserProfile.objects.get_or_create(user=user, defaults={'user_type': 'partner'})
        return user

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address")
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter first name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Enter last name")
    is_active = forms.BooleanField(required=False, help_text="Inactive users cannot log in")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
            
        if commit:
            user.save()
            # Ensure profile exists
            UserProfile.objects.get_or_create(user=user, defaults={'user_type': 'partner'})
        return user

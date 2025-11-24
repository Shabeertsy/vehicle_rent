from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Vehicle, Rental, Expense, UserProfile

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'registration_number', 'color', 'image', 'price_per_day']

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
            'customer_name', 'contact_no', 'customer_id', 'destination',
            'days_of_rent', 'rent_per_day', 'advance_amount',
            'starting_km', 'ending_km', 'total_amount_received', 'discounted_amount'
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
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep current password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Enter the new password again")

    # Permission fields
    can_manage_users = forms.BooleanField(required=False, help_text="Allow user to add, edit, and delete other users")
    can_manage_vehicles = forms.BooleanField(required=False, help_text="Allow user to add, edit, and delete vehicles")
    can_import_data = forms.BooleanField(required=False, help_text="Allow user to access import data functionality")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load current permissions from profile
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['can_manage_users'].initial = profile.can_manage_users
                self.fields['can_manage_vehicles'].initial = profile.can_manage_vehicles
                self.fields['can_import_data'].initial = profile.can_import_data
            except UserProfile.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Only reset permissions if not a superuser to avoid locking out admin
        if not user.is_superuser:
            user.is_staff = False
            user.is_superuser = False

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
            # Ensure profile exists and update permissions
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'user_type': 'partner'})
            profile.can_manage_users = self.cleaned_data.get('can_manage_users', False)
            profile.can_manage_vehicles = self.cleaned_data.get('can_manage_vehicles', False)
            profile.can_import_data = self.cleaned_data.get('can_import_data', False)
            profile.save()
        return user

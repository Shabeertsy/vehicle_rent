from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile for partners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, default='partner')  # All users are partners
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Partner"


# Signal to automatically create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, user_type='partner')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Vehicle(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., INNOVA 2014 V4")
    registration_number = models.CharField(max_length=20, unique=True, help_text="e.g., KL 10 BK 8469")
    color = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., SILVER")
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.registration_number}"


class Rental(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rentals', help_text="Partner responsible for this rental")
    date_out = models.DateField()
    time_out = models.TimeField(blank=True, null=True)
    date_in = models.DateField(blank=True, null=True)
    time_in = models.TimeField(blank=True, null=True)
    
    customer_name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    customer_id = models.CharField(max_length=50, blank=True, null=True)
    care_of = models.CharField(max_length=100, blank=True, null=True, verbose_name="C/O")
    destination = models.CharField(max_length=200, blank=True, null=True)
    
    days_of_rent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rent_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    starting_km = models.IntegerField(blank=True, null=True)
    ending_km = models.IntegerField(blank=True, null=True)
    
    total_amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.date_out}"
    
    @property
    def total_rent(self):
        return self.days_of_rent * self.rent_per_day

    @property
    def balance(self):
        # Assuming total_amount_received includes advance
        # Or should it be calculated? The prompt says "TOTAL CASH BLNCE" in the sheet.
        # Usually Balance = (Rent * Days) - Total Received.
        # But let's stick to storing what is given.
        return (self.days_of_rent * self.rent_per_day) - self.total_amount_received

class Expense(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses', help_text="Partner responsible for this expense")
    date = models.DateField()
    particulars = models.CharField(max_length=200)
    place = models.CharField(max_length=100, blank=True, null=True)
    care_of = models.CharField(max_length=100, blank=True, null=True, verbose_name="C/O")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.particulars} - {self.amount}"


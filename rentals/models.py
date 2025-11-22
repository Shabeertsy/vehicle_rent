from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, default='partner')
    taken_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Partner"


class Vehicle(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., INNOVA 2014 V4")
    registration_number = models.CharField(max_length=20, unique=True, help_text="e.g., KL 10 BK 8469")
    color = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., SILVER")
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    partners = models.ManyToManyField(User, related_name='vehicles')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.date_out}"

    @property
    def total_rent(self):
        return self.days_of_rent * self.rent_per_day

    @property
    def balance(self):
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


class TakenAmount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taken_amounts')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='taken_amounts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle.name} - {self.amount} on {self.date}"


class EMI(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='emi')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly EMI amount")
    due_day = models.IntegerField(default=1, help_text="Day of month when EMI is due (1-31)")
    warning_days = models.IntegerField(default=5, help_text="Days before due date to show warning")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EMI for {self.vehicle.name} - ₹{self.amount}"

    class Meta:
        verbose_name = "EMI"
        verbose_name_plural = "EMIs"


class EMIPayment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='emi_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    month_paid_for = models.DateField(help_text="The month this EMI is paid for (usually 1st of the month)")
    remarks = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EMI Payment - {self.vehicle.name} - {self.month_paid_for.strftime('%B %Y')}"

from django.contrib import admin
from .models import Vehicle, Rental, Expense, UserProfile

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(Rental)
admin.site.register(Expense)
admin.site.register(UserProfile)


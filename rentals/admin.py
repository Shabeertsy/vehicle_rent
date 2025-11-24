from django.contrib import admin
from .models import Vehicle, Rental, Expense, UserProfile

admin.site.register(Vehicle)
admin.site.register(Rental)
admin.site.register(Expense)
admin.site.register(UserProfile)


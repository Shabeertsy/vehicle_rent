from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Vehicle URLs
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/<int:pk>/partners/', views.vehicle_partners_get, name='vehicle_partners_get'),
    path('vehicles/<int:pk>/partners/update/', views.vehicle_partners_update, name='vehicle_partners_update'),
    path('vehicles/<int:pk>/pay-emi/', views.pay_emi, name='pay_emi'),
    path('emi/<int:pk>/delete/', views.delete_emi, name='delete_emi'),
    path('vehicles/<int:pk>/update-emi/', views.update_emi, name='update_emi'),
    path('vehicles/<int:pk>/export-excel/', views.vehicle_export_excel, name='vehicle_export_excel'),

    # Rental URLs
    path('vehicles/<int:vehicle_id>/rentals/add/', views.rental_create, name='rental_create'),
    path('rentals/<int:pk>/edit/', views.rental_edit, name='rental_edit'),
    path('rentals/<int:pk>/delete/', views.rental_delete, name='rental_delete'),

    # Expense URLs
    path('vehicles/<int:vehicle_id>/expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Import
    path('import/', views.import_data, name='import_data'),

    # User Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/update-taken-amount/', views.update_taken_amount, name='update_taken_amount'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
]


from django.urls import path
from bookings import views

urlpatterns = [
    path('create_booking/', views.create_booking, name='create_booking'),
]
from django.urls import path
from bookings import views

urlpatterns = [
    path('create_booking/', views.create_booking, name='create_booking'),
    path('get_booking_detail/', views.get_booking_detail, name='get_booking_detail'),
    path('send_ticket_api/', views.send_ticket_api, name='send_ticket_api'),
]
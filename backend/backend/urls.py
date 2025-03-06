from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('community/', include('community.urls')),
    path('events/', include('events.urls')),
    path('bookings/', include('bookings.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('payments/', include('payments.urls')),
]

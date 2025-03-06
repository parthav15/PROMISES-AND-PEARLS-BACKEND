from django.urls import path
from events.views import eventrequest_views

urlpatterns = [
    # EVENT REQUEST API's
    path('create_eventrequest/', eventrequest_views.create_eventrequest, name='create_eventrequest'),
    path('edit_eventrequest/<int:request_id>/', eventrequest_views.edit_eventrequest, name='edit_eventrequest'),
    path('delete_eventrequest/<int:request_id>/', eventrequest_views.delete_eventrequest, name='delete_eventrequest'),
    path('get_eventrequests_by_user/', eventrequest_views.get_eventrequests_by_user, name='get_eventrequests_by_user'),
]
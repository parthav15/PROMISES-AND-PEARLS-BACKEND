from django.urls import path
from admin_panel.views import admin_views, event_views, eventmedia_views, invitee_views

urlpatterns = [
    # ADMIN API's
    path('admin_login/', admin_views.admin_login, name='admin_login'),

    # EVENT API's
    path('create_event/', event_views.create_event, name='create_event'),
    path('get_all_events/', event_views.get_all_events, name='get_all_events'),
    path('get_event_by_id/<int:event_id>/', event_views.get_event_by_id, name='get_event_by_id'),
    path('update_event/<int:event_id>/', event_views.update_event, name='update_event'),
    path('delete_event/<int:event_id>/', event_views.delete_event, name='delete_event'),
    path('get_events_by_organizer/<int:user_id>/', event_views.get_events_by_organizer, name='get_events_by_organizer'),

    # EVENT MEDIA API's
    path('upload_event_images/', eventmedia_views.upload_event_images, name='upload_event_images'),
    path('get_all_images_for_event/', eventmedia_views.get_all_images_for_event, name='get_all_images_for_event'),
    path('delete_event_image/', eventmedia_views.delete_event_image, name='delete_event_image'),
    path('upload_event_video/', eventmedia_views.upload_event_video, name='upload_event_video'),
    path('get_all_videos_for_event/', eventmedia_views.get_all_videos_for_event, name='get_all_videos_for_event'),

    # INVITEE's API's
    path('add_invitees_to_event/<int:event_id>/', invitee_views.add_invitees_to_event, name='add_invitees_to_event'),
    path('get_invitees_for_event/<int:event_id>/', invitee_views.get_invitees_for_event, name='get_invitees_for_event'),
    path('update_invitee_status/<int:event_id>/<int:invitee_id>/', invitee_views.update_invitee_status, name='update_invitee_status'),
    path('remove_invitee_from_event/<int:event_id>/<int:invitee_id>/', invitee_views.remove_invitee_from_event, name='remove_invitee_from_event'),
]
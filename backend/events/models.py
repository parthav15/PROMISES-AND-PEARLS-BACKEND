from django.db import models
from users.models import CustomUser
import uuid

class Event(models.Model):
    PUBLIC = 'public'
    PRIVATE = 'private'
    EVENT_TYPES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'

    EVENT_STATUSES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=255, default='', blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default=PUBLIC)
    status = models.CharField(max_length=50, choices=EVENT_STATUSES, default=STATUS_PENDING)
    location = models.CharField(max_length=255, default='', blank=True, null=True)
    start_date = models.DateTimeField(default=None, blank=True, null=True)
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    event_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    max_attendees = models.PositiveIntegerField(default=0)
    current_attendees = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class Invitee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitees')
    email  = models.EmailField()
    name = models.CharField(max_length=255, default='', blank=True, null=True)
    invite_status = models.CharField(max_length=50, default='pending', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_images')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Image for {self.event.title}"
    
class EventVideo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_videos')
    video = models.FileField(upload_to='event_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Video for {self.event.title}"
    
class EventRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_requests')
    title = models.CharField(max_length=255, default='', blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    expected_start_date = models.DateTimeField(default=None, blank=True, null=True)
    expected_end_date = models.DateTimeField(default=None, blank=True, null=True)
    location = models.CharField(max_length=255, default='', blank=True, null=True)
    expected_guests = models.PositiveIntegerField(default=0)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
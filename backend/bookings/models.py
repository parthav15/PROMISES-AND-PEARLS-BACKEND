from django.db import models
from events.models import Event
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'

    BOOKING_STATUSES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    lead_user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='bookings')
    user_details = models.JSONField(blank=True, null=True)
    booking_status = models.CharField(max_length=50, choices=BOOKING_STATUSES, default=STATUS_PENDING)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_payment', unique=False)
    ticket_quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.id} - {self.user.email} for {self.event.title}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_booking')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transaction')
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.razorpay_payment_id} for Payment {self.payment.transaction_id}"

    class Meta:
        ordering = ['-created_at']

class Ticket(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    attendee = models.JSONField()
    qr_code = models.ImageField(upload_to='qrcodes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.ticket_id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_{self.ticket_id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
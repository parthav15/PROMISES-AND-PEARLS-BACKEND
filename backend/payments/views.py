from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import razorpay
from decimal import Decimal

from bookings.models import Payment, Transaction
from bookings.models import Booking
from bookings.views import send_ticket

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    currency = request.POST.get('currency', 'INR')
    booking_id = request.POST.get('booking_id')

    if not booking_id:
        return JsonResponse({'success': False, 'message': 'Amount and Booking ID are required.'}, status=400)
    
    booking = get_object_or_404(Booking, id=booking_id)

    amount = booking.total_price
    gst_amount = Decimal(0.18) * amount
    other_amount = Decimal(50)
    total_amount = amount + gst_amount + other_amount
    
    try:
        order_data = {
            'amount': int(Decimal(total_amount) * 100),
            'currency': currency,
            'receipt': str(booking_id),
            'payment_capture': 1
        }
        razorpay_order = client.order.create(data=order_data)

        payment = Payment.objects.create(
            booking=booking,
            amount=total_amount,
            status='Pending',
            transaction_id=razorpay_order['id']
        )

        booking.payment = payment
        booking.total_price = total_amount
        booking.save()

        return JsonResponse({
            'success': True,
            'message': 'Order created successfully.',
            'order_id': razorpay_order['id'],
            'amount': order_data['amount'],
            'currency': currency,
            'payment_id': payment.id
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating order: {str(e)}'}, status=400)


@csrf_exempt
def verify_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({'success': False, 'message': 'All payment details are required.'}, status=400)

    try:
        client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature,
        })

        payment = get_object_or_404(Payment, transaction_id=razorpay_order_id)
        payment.status = 'Completed'
        payment.save()

        booking = payment.booking
        booking.booking_status = Booking.STATUS_CONFIRMED
        booking.save()

        transaction = Transaction.objects.create(
            payment=payment,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_signature=razorpay_signature
        )

        try:
            send_ticket(booking.event, booking)
        except Exception as e:
            print(f"Error sending ticket: {str(e)}")

        return JsonResponse({
            'success': True,
            'message': 'Payment verified successfully.',
            'transaction_id': transaction.id
        }, status=200)

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'message': 'Payment verification failed.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error verifying payment: {str(e)}'}, status=400)

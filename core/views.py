from django.shortcuts import render, redirect, get_object_or_404
from booking.models import *
from payments.models import *
import uuid
from django.http import HttpResponse
import requests
from django.conf import settings
import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required() #add signup logic
def home(request):
    return render(request, 'core/home.html')

def search_buses(request):
    schedules = Schedule.objects.none()
    if request.method == 'POST':
        origin          = request.POST.get('origin')
        destination     = request.POST.get('destination')
        travel_date     = request.POST.get('travel_date')

        if origin and destination and travel_date:
            schedules = Schedule.objects.filter(
            route__origin__iexact = origin,
            route__destination__iexact = destination,
            travel_date = travel_date
            )

    context={
        'schedules': schedules,
    }

    return render(request, 'booking/search_buses.html', context)

@login_required()
def select_seat(request, schedule_id):
    schedule = get_object_or_404(Schedule,id=schedule_id)
    seats = Seat.objects.filter(bus=schedule.bus)

    Booking.objects.filter(expires_at__lt=timezone.now(), booking_status='Pending').update(booking_status='Cancelled')

    booked_seats = Booking.objects.filter(schedule=schedule).filter(Q(booking_status='Confirmed') | Q(booking_status='Pending', expires_at__gt=timezone.now())).values_list('seat_id', flat=True)

    context = {
        'seats': seats,
        'schedule': schedule,
        'booked_seats':booked_seats,
    }
    return render(request, 'booking/select_seat.html', context)

#booking
@login_required()
def book_seat(request, schedule_id, seat_id):
    schedule            = get_object_or_404(Schedule, id=schedule_id)
    seat                = get_object_or_404(Seat, id=seat_id)
    customer            = request.user.customer
    booking_reference   = str(uuid.uuid4())[:8].upper()

    with transaction.atomic():
        # check if exists
        seat = Seat.objects.select_for_update().get(id=seat_id)
        exists = Booking.objects.filter(schedule=schedule, seat=seat).filter(Q(booking_status='Pending', expires_at__gt=timezone.now()) | Q(booking_status='Confirmed')).exists()

        if exists:
            return HttpResponse("Already booked")

        booking = Booking.objects.create(customer=customer, schedule=schedule, seat=seat, booking_reference=booking_reference, expires_at=timezone.now() + timedelta(minutes=2))
    
    return redirect('initialize_payment', booking_id=booking.id)

#  describe  payments logics
def initialize_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    email = request.user.email
    amount = int(booking.schedule.price * 100) # convert to kobo
    if booking.expires_at < timezone.now():
        return HttpResponse('Booking expired. Start again') # computer is not running this line of code

    url = 'https://api.paystack.co/transaction/initialize'

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'email': email,
        'amount': amount,
        'callback_url': request.build_absolute_uri('/payment/verify/')
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status']:
        payment_url = response_data['data']['authorization_url']
        reference = response_data['data']['reference']
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.schedule.price,
            transaction_id=reference,
            payment_status='Pending'
        )

        return redirect(payment_url)
    else:
        return HttpResponse("Payment initialization failed")
    
@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.header.get('x-paystack-signature')
    computed_signature = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), payload, hashlib.sha512).hexdigest()

    # verify signature
    if signature != computed_signature:
        return HttpResponse(status=400)
    
    data = json.loads(payload)

    if data['event'] == 'charge.success':
        reference = data['data']['reference']

        payment = get_object_or_404(Payment, transaction_id=reference)
        booking = payment.booking
        if booking.expires_at < timezone.now():
            payment.payment_status = 'Failed'
            payment.save()

            return HttpResponse(status=200) # still return 200 to Paystack

        # Only valid bookings continue
        # payment.payment_status = 'Paid'
        # payment.save()

        # booking = payment.booking
        # booking.booking_status = 'Confirmed'
        # booking.save()
    
    elif data['event'] == 'refund.processed':
        refund_reference = data['data']['transaction_reference']
        print(data)

        refund = Refund.objects.filter(refund_reference=refund_reference).first()

        if refund:
            refund.refund_status = 'Refunded'
            refund.save()
        
        return HttpResponse(status=200)
    
    return HttpResponse(status=200)


def verify_payment(request):
    reference = request.GET.get('reference')

    payment = Payment.objects.filter(transaction_id=reference).first()

    if payment and payment.payment_status == 'Paid':
        return HttpResponse('Payment already confirmed')

    url = f'https://api.paystack.co/transaction/verify/{reference}'

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data['status']:
        payment_data = response_data['data']

        if payment_data['status'] == 'success':
            payment = Payment.objects.filter(transaction_id=reference).first()

            if not payment:
                return HttpResponse('Invalid or missing payment record')

            payment.payment_status = 'Paid'
            payment.save()

            booking = payment.booking
            booking.booking_status = 'Confirmed'
            booking.save()

            return redirect('create_ticket', booking_id=booking.id)
        
    return HttpResponse("payment failed")

@login_required()
def create_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    ticket_number = f"TKT-{booking.booking_reference}"

    ticket, created = Ticket.objects.get_or_create(booking=booking, defaults={'ticket_number': ticket_number})

    context = {
        'ticket': ticket,
    }

    return render(request, 'booking/create_ticket.html', context)

def verify_ticket(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    context = {
        'ticket':ticket,
    }
    return render(request, 'booking/verify_ticket.html', context)


# ----------REPORT GENERATIONS ------------

def booking_report(request):
    bookings = Booking.objects.all().order_by('-booked_at')

    context = {
        'bookings':bookings
    }
    return render(request, 'booking/booking_report.html', context)

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = booking.payment

    if payment.payment_status != 'Paid':
        return HttpResponse('Can not refund unpaid booking')
    
    if Refund.objects.filter(payment=payment).exists():
        return HttpResponse('Refund already requested')
    
    url = 'https://api.paystack.co/refund'

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'transaction': payment.transaction_id,
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    print(response_data)
    print(response_data)

    if response_data['status']:
        Refund.objects.create(payment=payment, refund_reference=response_data['data']['id'], amount=payment.amount, refund_status='Pending')

        booking.booking_status='Cancelled'
        booking.save()

        return redirect('booking_report')
    
    return HttpResponse('Refund failed')
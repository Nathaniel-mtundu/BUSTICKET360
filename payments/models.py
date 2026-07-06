from django.db import models
from booking.models import *

# Create your models here.

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('M-Pesa', 'M-Pesa'),
        ('Mixxed by yas', 'Mixxed by yas'),
        ('Airtel Money', 'Airtel Money'),
        ('HaloPesa', 'HaloPesa'),
    )
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    booking                    = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount                     = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method             = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id             = models.CharField(max_length=100, unique=True)
    payment_status             = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    paid_at                    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id
    
class Refund(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Refunded', 'Refunded'),
        ('Failed', 'Failed')
    )

    payment                     = models.OneToOneField(Payment, on_delete=models.CASCADE)
    refund_reference            = models.CharField(max_length=100)
    amount                      = models.DecimalField(max_digits=10, decimal_places=2)
    refund_status               = models.CharField(max_length=20, choices=STATUS, default='Pending')
    created_at                  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.refund_reference
from django.db import models
from accounts.models import Customer
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
from django.core.files import File

# Create your models here.

# ------------BUS COMPANY-------------
class BusCompany(models.Model):
    name                        = models.CharField(max_length=100)
    logo                        = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    phone_number                = models.CharField(max_length=20)
    email                       = models.EmailField(blank=True)
    address                     = models.CharField(max_length=255, blank=True)
    created_at                  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
#-------------BUS----------------
class Bus(models.Model):
    BUS_TYPE = (
        ('Normal', 'Normal'),
        ('VIP', 'VIP')
    )

    company                         = models.ForeignKey(BusCompany, on_delete=models.CASCADE)
    plate_number                    = models.CharField(max_length=50, unique=True)
    bus_name                        = models.CharField(max_length=100)
    total_seats                     = models.PositiveIntegerField()
    bus_type                        = models.CharField(max_length=20, choices=BUS_TYPE)
    image                           = models.ImageField(upload_to='bus_images/', null=True, blank=True)
    created_at                      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_name} ({self.plate_number})"
    
class Route(models.Model):
    origin                      = models.CharField(max_length=100)
    destination                 = models.CharField(max_length=100)
    distance_km                 = models.PositiveIntegerField(null=True, blank=True)
    estimated_duration          = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.origin} -> {self.destination}"

class Schedule(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Boarding', 'Boarding'),
        ('Departed', 'Departed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    bus                         = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route                       = models.ForeignKey(Route, on_delete=models.CASCADE)
    travel_date                 = models.DateField()
    departure_time              = models.TimeField()
    arrival_time                = models.TimeField()
    price                       = models.DecimalField(max_digits=10, decimal_places=2)
    status                      = models.CharField(
                                        max_length=20,
                                        choices=STATUS_CHOICES,
                                        default='Scheduled'
                                    )
    is_available                = models.BooleanField(default=True)
    created_at                  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.route} | {self.travel_date}"
    
class Seat(models.Model):
    bus                         = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number                 = models.CharField(max_length=10)
    is_window                   = models.BooleanField(default=False)
    created_at                  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus.bus_name} - {self.seat_number}"

class Booking(models.Model):
    BOOKING_STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )
    customer                    = models.ForeignKey(Customer, on_delete=models.CASCADE)
    schedule                    = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat                        = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking_status              = models.CharField(max_length=20, choices=BOOKING_STATUS, default='Pending')
    booking_reference           = models.CharField(max_length=100, unique=True)
    expires_at                  = models.DateTimeField()
    booked_at                   = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ('schedule', 'seat')

    def __str__(self):
        return f"{self.customer} - {self.booking_reference}"
    
class Ticket(models.Model):
    booking                     = models.OneToOneField(Booking, on_delete=models.CASCADE)
    ticket_number               = models.CharField(max_length=100, unique=True)
    qr_code                     = models.ImageField(upload_to='ticket_qr/', null=True, blank=True)
    created_at                  = models.DateTimeField(auto_now_add=True)

    def generate_qr_code(self):
        url = f"http://192.168.0.11:8000/tickets/verify_ticket/{self.ticket_number}/"

        qr_img = qrcode.make(url)

        buffer = BytesIO()
        qr_img.save(buffer)
        buffer.seek(0)

        file_name = f"{self.ticket_number}.png"

        self.qr_code.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()

        super().save(*args, **kwargs) 

    def __str__(self):
        return self.ticket_number

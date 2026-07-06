from django.urls import path
from . import views, api_views
urlpatterns = [
    path('',  views.home, name='home'),
    path('search_buses/', views.search_buses, name='search_buses'),
    path('select_seat/<int:schedule_id>/', views.select_seat, name='select_seat'),
    path('book_seat/<int:schedule_id>/<int:seat_id>/', views.book_seat, name='book_seat'),
    path('payment/<int:booking_id>/', views.initialize_payment, name='initialize_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/paystack_webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('tickets/<int:booking_id>/', views.create_ticket, name='create_ticket'),
    path('tickets/verify_ticket/<str:ticket_number>/', views.verify_ticket, name='verify_ticket'),
    path('booking/booking_report/', views.booking_report, name='booking_report'),
    path('booking/cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/schedules/', api_views.schedule_list, name='schedule_list'),
    path('api/seat_list/', api_views.seat_list, name='seat_list'),
    path('api/create_schedule/', api_views.create_schedule, name='create_schedule'),
    path('api/route_list/', api_views.route_list, name='route_list'),
    path('api/bus_list/', api_views.bus_list, name='bus_list'),
    path('api/update_schedule/<int:schedule_id>/', api_views.update_schedule, name='update_schedule'),
]

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import *
from accounts.models import *
from payments.models import *
from booking.models import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def schedule_list(request):
    schedules = Schedule.objects.all()
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seat_list(request):
    seats = Seat.objects.all()
    serializer = SeatSerializer(seats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def route_list(request):
    routes = Route.objects.all()
    serializer = RouteSerializer(routes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bus_list(request):
    buses = Bus.objects.all()
    serializer = BusSerializer(buses, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    schedule = ScheduleSerializer(data = request.data)
    if schedule.is_valid():
        schedule.save()
        return Response(schedule.data, status=status.HTTP_201_CREATED)
    return Response(schedule.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    serializer = ScheduleSerializer(instance=schedule, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
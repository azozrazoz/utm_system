from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import Drone, DroneLocation, Pilot, FlightRoute, NoFlyZone, FlightPermission
from .serializers import DroneSerializer, DroneLocationSerializer
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
import threading, time
import random
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import FlightRouteForm, DroneRegistrationForm, FlightPermissionForm
from django.contrib.gis.geos import GEOSGeometry
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from django.utils.timezone import now
from django.core.serializers import serialize
from .models import NoFlyZone

User = get_user_model()

class DroneViewSet(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    

class DroneLocationViewSet(viewsets.ModelViewSet):
    queryset = DroneLocation.objects.all()
    serializer_class = DroneLocationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    

class MapView(TemplateView):
    template_name = 'map.html'

@api_view(['GET'])
def drone_locations_api(request):
    from .serializers import DroneLocationSerializer
    locations = DroneLocation.objects.all()
    serializer = DroneLocationSerializer(locations, many=True)
    return Response(serializer.data)

def get_last_location(request):
    last = DroneLocation.objects.last()
    if last:
        return JsonResponse({'latitude': last.latitude, 'longitude': last.longitude})
    return JsonResponse({})

@csrf_exempt
def start_emulation(request):
    def emulate():
        drone = Drone.objects.first()
        lat, lng = 51.1605, 71.4704
        for _ in range(50):
            lat += random.uniform(-0.0005, 0.0005)
            lng += random.uniform(-0.0005, 0.0005)
            DroneLocation.objects.create(drone=drone, latitude=lat, longitude=lng)
            time.sleep(2)
    threading.Thread(target=emulate).start()
    return JsonResponse({'status': 'started'})

class PilotRegisterView(APIView):
    def get(self, request):
        return render(request, 'register_pilot.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact_phone = request.POST.get('contact_phone')
        license_number = request.POST.get('license_number')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Имя пользователя уже занято.')
            return redirect('register_pilot')

        if Pilot.objects.filter(license_number=license_number).exists():
            messages.error(request, 'Пилот с таким номером лицензии уже существует.')
            return redirect('register_pilot')

        user = User.objects.create_user(username=username, email=email, password=password, is_pilot=True)
        user.save()

        Pilot.objects.create(user=user, contact_phone=contact_phone, license_number=license_number)

        messages.success(request, 'Пилот успешно зарегистрирован!')
        return redirect('login')
    
    
def home_view(request):
    return render(request, 'home.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            if user.is_pilot:
                return redirect('pilot_dashboard')
            elif user.is_operator:
                return redirect('operator_dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def pilot_dashboard(request):
    try:
        pilot = request.user.pilot_profile
    except Pilot.DoesNotExist:
        return render(request, 'pilot_dashboard.html', {
            'error': 'Профиль пилота не найден.'
        })

    flights = FlightRoute.objects.filter(pilot=pilot).order_by('-created_at')

    return render(request, 'pilot_dashboard.html', {
        'flights': flights,
    })

def is_operator(user):
    return user.groups.filter(name='Operators').exists()  # или другая логика

@login_required
def operator_dashboard(request):
    permissions = FlightPermission.objects.select_related('flight_route', 'flight_route__pilot').filter(status='pending')
    return render(request, 'operator_dashboard.html', {'permissions': permissions})


@login_required
def review_flight_permission(request, route_id):
    permission = get_object_or_404(FlightPermission, id=route_id)

    if request.method == 'POST':
        form = FlightPermissionForm(request.POST, instance=permission)
        if form.is_valid():
            perm = form.save(commit=False)
            perm.operator = request.user
            perm.reviewed_at = now()
            perm.save()
            
            route = perm.flight_route
            route.status = perm.status
            route.save()
            
            return redirect('operator_dashboard')
    else:
        form = FlightPermissionForm(instance=permission)

    return render(request, 'review_permission.html', {
        'permission': permission,
        'form': form,
        'route': permission.flight_route
    })

async def simulate_flight(flight_id, coordinates):
    channel_layer = get_channel_layer()
    group_name = f'flight_{flight_id}'

    for coord in coordinates:
        await channel_layer.group_send(
            group_name,
            {
                'type': 'drone_position',
                'latitude': coord[1],  # Координаты geojson в формате [lon, lat]
                'longitude': coord[0],
            }
        )
        await asyncio.sleep(1)  # Задержка 1 секунда между координатами
        
        
def start_flight(request, flight_id):
    flight = FlightRoute.objects.get(pk=flight_id)
    # Предполагается, что flight.route — это GeoDjango LineStringField

    # Получаем координаты маршрута
    coords = list(flight.route.coords)

    async_to_sync(simulate_flight)(flight_id, coords)

    return redirect('pilot_dashboard')

@login_required
def create_flight_route(request):
    try:
        pilot = request.user.pilot_profile
    except Pilot.DoesNotExist:
        return render(request, 'create_flight.html', {'error': 'Профиль пилота не найден.'})

    if request.method == 'POST':
        form = FlightRouteForm(request.POST)
        # Ограничиваем queryset для выбора дронов пилота
        form.fields['drone'].queryset = Drone.objects.filter(pilot=request.user)
        geojson_path = request.POST.get('path')  # GeoJSON string
        if form.is_valid() and geojson_path:
            route = form.save(commit=False)
            route.pilot = pilot
            route.status = 'pending'
            try:
                route.path = GEOSGeometry(geojson_path)  # Преобразуем GeoJSON в геометрию
                route.save()
                FlightPermission.objects.create(flight_route=route, status='pending')
                return redirect('pilot_dashboard')
            except Exception as e:
                form.add_error(None, f"Ошибка обработки маршрута: {e}")
    else:
        form = FlightRouteForm()
        form.fields['drone'].queryset = Drone.objects.filter(pilot=request.user)

    return render(request, 'create_flight.html', {'form': form})

@login_required
def view_flight(request, flight_id):
    flight = get_object_or_404(FlightRoute, id=flight_id, pilot__user=request.user)
    return render(request, 'view_flight.html', {'flight': flight, 'path_geojson': flight.path.geojson if flight.path else None})

@login_required
def register_drone(request):
    if request.method == 'POST':
        form = DroneRegistrationForm(request.POST)
        if form.is_valid():
            drone = form.save(commit=False)
            drone.pilot = request.user
            drone.save()
            return redirect('pilot_dashboard')
    else:
        form = DroneRegistrationForm()
    return render(request, 'register_drone.html', {'form': form})

@login_required
def no_fly_zones_page(request):
    zones = NoFlyZone.objects.all()
    zones_geojson = serialize('geojson', zones, geometry_field='area', fields=('name', 'description', 'restriction_level', 'start_time', 'end_time'))
    return render(request, 'no_fly_zones.html', {
        'zones': zones,
        'zones_geojson': zones_geojson
    })
from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings


class User(AbstractUser):
    is_pilot = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Pilot(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pilot_profile')
    full_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    completed_routes_count = models.PositiveIntegerField(default=0)  # количество пройденных маршрутов

    def __str__(self):
        return self.full_name
    

class Drone(models.Model):
    pilot = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Пилот"
    )
    unique_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный номер"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Название"
    )
    drone_type = models.CharField(
        max_length=50,
        default="QUAD",
        verbose_name="Тип БПЛА"
    )
    max_altitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Максимальная высота (м)"
    )
    max_speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Максимальная скорость (км/ч)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Беспилотник"
        verbose_name_plural = "Беспилотники"

    def __str__(self):
        return f"{self.name} ({self.unique_number})"
    

class DroneLocation(models.Model):
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = gis_models.PointField(geography=True)

    def __str__(self):
        return f"{self.drone.name} at {self.timestamp}"
    

class NoFlyZone(models.Model):
    RESTRICTION_LEVELS = [
        ('strict', 'Strict'),
        ('conditional', 'Conditional'),
        ('allowed', 'Allowed'),
    ]

    name = models.CharField(max_length=100)
    area = gis_models.PolygonField()
    description = models.TextField(blank=True)
    restriction_level = models.CharField(max_length=20, choices=RESTRICTION_LEVELS, default='strict')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class FlightRoute(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('violated', 'Violated'),
    ]

    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, related_name='flight_routes')
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='flight_routes')
    path = gis_models.LineStringField()
    altitude = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mission_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Route #{self.id} by {self.pilot.full_name}"


class FlightPermission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    flight_route = models.OneToOneField(FlightRoute, on_delete=models.CASCADE, related_name='permission')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='flight_permissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Permission for route #{self.flight_route.id}: {self.status}"


class FlightViolationLog(models.Model):
    flight_route = models.ForeignKey(FlightRoute, on_delete=models.CASCADE, related_name='violations')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = gis_models.PointField()
    description = models.TextField()
    notified_operator = models.BooleanField(default=False)

    def __str__(self):
        return f"Violation on route #{self.flight_route.id} at {self.timestamp}"

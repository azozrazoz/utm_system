# utm/admin.py
from django.contrib import admin
from .models import Drone, DroneLocation, User, Pilot, NoFlyZone, FlightRoute, FlightPermission, FlightViolationLog

admin.site.register(Drone)
admin.site.register(DroneLocation)
admin.site.register(User)
admin.site.register(Pilot)
admin.site.register(NoFlyZone)
admin.site.register(FlightRoute)
admin.site.register(FlightPermission)
admin.site.register(FlightViolationLog)

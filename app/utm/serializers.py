from rest_framework import serializers
from .models import Drone, DroneLocation, User, Pilot
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
import re

class PilotRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'contact_phone', 'is_pilot')

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        contact_phone = validated_data['contact_phone']
        license_number = validated_data['license_number']

        user = User.objects.create_user(contact_phone=contact_phone, username=username, email=email, password=password)
        pilot = Pilot.objects.create(
            is_pilot=True,
            user=user,
            contact_phone=contact_phone,
            license_number=license_number,
            completed_routes=0
        )
        return pilot
    
    def validate_contact_phone(self, value):
        # Пример валидации формата телефона: только цифры, 10-15 символов
        if not re.match(r'^\+?\d{10,15}$', value):
            raise serializers.ValidationError("Некорректный номер телефона.")
        return value

    def validate_license_number(self, value):
        # Лицензия должна содержать ровно 5 цифр
        if not re.match(r'^\d{5}$', value):
            raise serializers.ValidationError("Номер лицензии должен содержать ровно 5 цифр.")
        return value


class DroneLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = DroneLocation
        geo_field = 'location'  # указываем гео-поле
        fields = ('id', 'drone', 'location', 'timestamp')

class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = '__all__'

class DroneLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = DroneLocation
        geo_field = 'location'  # поле с PointField
        fields = ('id', 'drone', 'timestamp', 'location')
        
    def create(self, validated_data):
        location_data = validated_data.pop("location")
        if isinstance(location_data, dict):
            coords = location_data.get("coordinates")
            if not coords or len(coords) != 2:
                raise serializers.ValidationError("Invalid GeoJSON point format")
            validated_data["location"] = Point(coords[0], coords[1])
        else:
            raise serializers.ValidationError("Location must be a GeoJSON dict")
        
        return DroneLocation.objects.create(**validated_data)
        
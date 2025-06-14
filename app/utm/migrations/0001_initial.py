# Generated by Django 5.2.1 on 2025-05-24 15:02

import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoFlyZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('area', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('description', models.TextField(blank=True)),
                ('restriction_level', models.CharField(choices=[('strict', 'Strict'), ('conditional', 'Conditional'), ('allowed', 'Allowed')], default='strict', max_length=20)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_pilot', models.BooleanField(default=False)),
                ('is_operator', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Drone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_number', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('drone_type', models.CharField(default='QUAD', max_length=50)),
                ('max_altitude', models.FloatField(blank=True, null=True)),
                ('max_speed', models.FloatField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('pilot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DroneLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('drone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utm.drone')),
            ],
        ),
        migrations.CreateModel(
            name='FlightRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('altitude', models.FloatField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('violated', 'Violated')], default='pending', max_length=20)),
                ('rejection_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mission_type', models.CharField(blank=True, max_length=50)),
                ('drone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_routes', to='utm.drone')),
            ],
        ),
        migrations.CreateModel(
            name='FlightPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('comments', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flight_permissions', to=settings.AUTH_USER_MODEL)),
                ('flight_route', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='permission', to='utm.flightroute')),
            ],
        ),
        migrations.CreateModel(
            name='FlightViolationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('description', models.TextField()),
                ('notified_operator', models.BooleanField(default=False)),
                ('flight_route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='violations', to='utm.flightroute')),
            ],
        ),
        migrations.CreateModel(
            name='Pilot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('contact_phone', models.CharField(blank=True, max_length=20)),
                ('completed_routes_count', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pilot_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='flightroute',
            name='pilot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_routes', to='utm.pilot'),
        ),
    ]

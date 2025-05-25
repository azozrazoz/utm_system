from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, FlightRoute, Drone, FlightPermission

class PilotRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_pilot = True
        if commit:
            user.save()
        return user

class FlightRouteForm(forms.ModelForm):
    class Meta:
        model = FlightRoute
        exclude = ['pilot', 'status', 'rejection_reason', 'created_at', 'updated_at']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
class FlightPlanForm(forms.ModelForm):
    class Meta:
        model = FlightRoute
        fields = ['drone', 'altitude', 'start_time', 'end_time', 'mission_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drone'].widget.attrs.update({'class': 'form-select'})
        self.fields['altitude'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['mission_type'].widget.attrs.update({'class': 'form-select'})
        

class DroneRegistrationForm(forms.ModelForm):
    class Meta:
        model = Drone
        fields = ['unique_number', 'name', 'drone_type', 'max_altitude', 'max_speed', 'description']
        widgets = {
            'unique_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'drone_type': forms.TextInput(attrs={'class': 'form-control'}),
            'max_altitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'max_speed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    

class FlightPermissionForm(forms.ModelForm):
    class Meta:
        model = FlightPermission
        fields = ['status', 'comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
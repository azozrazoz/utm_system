# utm/urls.py
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import DroneViewSet, DroneLocationViewSet, MapView, drone_locations_api, start_emulation, PilotRegisterView
from . import views
from . import consumers
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'drones', DroneViewSet)
router.register(r'dronelocations', DroneLocationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('map/', MapView.as_view(), name='map'),
    path('api/dronelocations/', drone_locations_api, name='drone-locations-api'),
    path('start-emulation/', start_emulation, name='start_emulation'),
    path('register/pilot/', PilotRegisterView.as_view(), name='register_pilot'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pilot/dashboard/', views.pilot_dashboard, name='pilot_dashboard'),
    path('pilot/create-flight/', views.create_flight_route, name='create_flight'),
    path('pilot/flight/<int:flight_id>/', views.view_flight, name='view_flight'),
    
    path('register-drone/', views.register_drone, name='register_drone'),
    
    
    path('operator/dashboard/', views.operator_dashboard, name='operator_dashboard'),
    path('operator/review/<int:route_id>/', views.review_flight_permission, name='review_flight_permission'),
    path('no-fly-zones/page/', views.no_fly_zones_page, name='no_fly_zones_page'),
    
    re_path(r'ws/drone/(?P<flight_id>\d+)/$', consumers.DroneConsumer.as_asgi()),
]
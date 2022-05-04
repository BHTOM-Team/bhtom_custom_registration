from django.contrib.auth.views import LoginView
from django.urls import path

from bhtom_custom_registration.bhtom_registration.registration_flows.open.views import OpenRegistrationView

app_name = 'bhtom_custom_registration.bhtom_registration'


urlpatterns = [
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/register/', OpenRegistrationView.as_view(), name='register'),
]

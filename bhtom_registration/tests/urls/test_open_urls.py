from django.urls import include, path

app_name = 'bhtom_custom_registration.bhtom_registration'


urlpatterns = [
    path('', include('bhtom_custom_registration.bhtom_registration.registration_flows.open.urls', namespace='registration')),
    path('', include('bhtom_base.bhtom_common.urls')),
]

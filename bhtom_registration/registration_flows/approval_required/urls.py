from django.contrib.auth.views import LoginView
from django.urls import path

from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.forms import ApprovalAuthenticationForm
from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views import ApprovalRegistrationView, UserApprovalView, AcceptTerms

app_name = 'bhtom_custom_registration.bhtom_registration'


urlpatterns = [
    path('accounts/login/', LoginView.as_view(authentication_form=ApprovalAuthenticationForm), name='login'),
    path('accounts/register/', ApprovalRegistrationView.as_view(), name='register'),
    path('accounts/approve/<int:pk>/', UserApprovalView.as_view(), name='approve'),
    path("terms/", AcceptTerms.as_view(), name="terms")
]

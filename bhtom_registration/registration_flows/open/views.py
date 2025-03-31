from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView
from django.shortcuts import redirect,render
from django.urls import reverse_lazy
from django.shortcuts import render
from bhtom2.utils.bhtom_logger import BHTOMLogger
from bhtom_custom_registration.bhtom_registration.registration_flows.open.forms import OpenRegistrationForm

logger: BHTOMLogger = BHTOMLogger(__name__, 'Bhtom: bhtom_registration')


class OpenRegistrationView(CreateView):
    """
    View for registering in the open registration flow. This view creates the user, adds them to the public group, and
    immediately logs them in.
    """
    template_name = 'bhtom_registration/register_user.html'
    success_url = reverse_lazy(settings.TOM_REGISTRATION.get('REGISTRATION_REDIRECT_PATTERN', ''))
    form_class = OpenRegistrationForm

    def form_valid(self, form):
        super().form_valid(form)
        group, _ = Group.objects.get_or_create(name='Public')
        group.user_set.add(self.object)
        group.save()

        messages.info(self.request, 'Registration was successful!')
        if isinstance(self.object, User):
            try:
                login(self.request, self.object,
                      backend=settings.TOM_REGISTRATION.get('REGISTRATION_AUTHENTICATION_BACKEND'))
            except ValueError as ve:
                logger.error(f'Unable to log in newly registered user: {ve}')

        return redirect(self.get_success_url())

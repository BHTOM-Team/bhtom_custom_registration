import os
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from dotenv import dotenv_values

from bhtom2.settings import BASE_DIR
from bhtom2.utils.bhtom_logger import BHTOMLogger
from bhtom_base.bhtom_common.mixins import SuperuserRequiredMixin
from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.forms import ApproveUserForm
from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.forms import RegistrationApprovalForm

logger: BHTOMLogger = BHTOMLogger(__name__, 'Bhtom: bhtom_registration')
secret = dotenv_values(os.path.join(BASE_DIR, 'bhtom2/.bhtom.env'))


# TODO: Add post-approval hooks that actually handle the sending of email
class ApprovalRegistrationView(CreateView):
    """
    View for handling registration requests in the approval required registration flow. This flow creates users but sets
    them as inactive, requiring administrator approval in order to log in. Upon registration, an email is sent to the
    administrators of the TOM informing them of the request.
    """
    template_name = 'bhtom_registration/register_user.html'
    success_url = reverse_lazy(settings.TOM_REGISTRATION.get('REGISTRATION_REDIRECT_PATTERN', ''))
    form_class = RegistrationApprovalForm

    def form_valid(self, form):
        super().form_valid(form)
        group, _ = Group.objects.get_or_create(name='Public')
        group.user_set.add(self.object)
        group.save()

        messages.info(self.request, 'Your request to register has been submitted to the administrators.')

        if settings.TOM_REGISTRATION.get('SEND_APPROVAL_EMAILS'):
            try:
                send_mail(secret.get("EMAILTET_ACTIVATEUSER_TITLE", "Account activation"),
                          secret.get('EMAILTEXT_REGISTEUSER'),
                          settings.EMAIL_HOST_USER, [user_email.email], fail_silently=False)

                logger.info('Create User' + instance.obsName + ', Send mail: ' + user_email.email)

            except SMTPException as smtpe:
                logger.error(f'Unable to send email: {smtpe}')

        return redirect(self.get_success_url())


class UserApprovalView(SuperuserRequiredMixin, UpdateView):
    """
    View for approving (activating) pending (inactive) users in the approval required registration flow. Upon approval,
    an email is sent to the user informing them of the registration approval.
    """
    model = User
    template_name = 'bhtom_registration/approve_user.html'
    success_url = reverse_lazy('user-list')
    form_class = ApproveUserForm

    def form_valid(self, form):
        response = super().form_valid(form)

        if settings.TOM_REGISTRATION.get('SEND_APPROVAL_EMAILS'):
            try:
                current_domain = Site.objects.get_current().domain
                link_to_login = f'https://{current_domain}{reverse("login")}'
                send_mail(settings.TOM_REGISTRATION.get('APPROVAL_SUBJECT', 'Your registration has been approved!'),
                          settings.TOM_REGISTRATION.get('APPROVAL_MESSAGE',
                                                        'Your registration has been approved. You can log in '
                                                        f'<a href="{link_to_login}">here</a>.'),
                          settings.SERVER_EMAIL,
                          [self.object.email],
                          fail_silently=False)
            except SMTPException as smtpe:
                logger.error(f'Unable to send email: {smtpe}')

        return response

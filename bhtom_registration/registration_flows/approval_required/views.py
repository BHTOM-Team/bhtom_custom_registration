
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from bhtom_custom_registration.bhtom_registration.models import LatexUser
from bhtom2.utils.bhtom_logger import BHTOMLogger
from bhtom_base.bhtom_common.mixins import SuperuserRequiredMixin
from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.forms import ApproveUserForm
from bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.forms import RegistrationApprovalForm

logger: BHTOMLogger = BHTOMLogger(__name__, 'Bhtom: bhtom_registration')


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

        
        try:
            email_params = "'{0}', '{1}', '{2}', '{3}', 'https://bh-tom2.astrolabs.pl/users/'".format(self.object.username, self.object.first_name,
                                                           self.object.last_name, self.object.email)
            send_mail(settings.EMAILTEXT_REGISTEADMIN_TITLE, settings.EMAILTEXT_REGISTEADMIN + email_params,
                      settings.EMAIL_HOST_USER,
                      settings.RECIPIENTEMAIL, fail_silently=False)

            send_mail(settings.EMAILTEXT_REGISTEUSER_TITLE, settings.EMAILTEXT_REGISTEUSER, settings.EMAIL_HOST_USER,
                      [self.object.email], fail_silently=False)
        except Exception as e:
            logger.error(f'Exception when sending registration confirmation: {e}')

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
        return response

class AcceptTerms(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            user_info = LatexUser.objects.get(user=request.user)
            user_info.accepted_terms = True
            user_info.save()
            messages.success(request, "Terms & Conditions accepted successfully.")
        except LatexUser.DoesNotExist:
            messages.error(request, "User profile not found.")
            logger.error(f"LatexUser profile not found for user {request.user}")
        except Exception as e:
            messages.error(request, "An error occurred while accepting the terms.")
            logger.error(f"Error updating terms acceptance for user {request.user}: {e}")

        return redirect("/")

    def get(self, request, *args, **kwargs):
        return render(request, "terms.html")
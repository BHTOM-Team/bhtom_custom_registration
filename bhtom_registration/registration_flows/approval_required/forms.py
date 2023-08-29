from django import forms
from django.contrib.auth.forms import AuthenticationForm

from bhtom_base.bhtom_common.forms import CustomUserCreationForm
from bhtom_custom_registration.bhtom_registration.models import LatexUser

class RegistrationApprovalForm(CustomUserCreationForm):
    """
    Form for handling registration requests in the approval required registration flow. Sets the user to inactive.
    """
    latex_name = forms.CharField(required=True, label='Latex Name*',
                                 help_text="Your name as you want it to appear correctly in potential publications")
    latex_affiliation = forms.CharField(required=True, label='Latex Affiliation*',
                                        help_text="Your affiliation as you want it to appear correctly in potential publications")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            user = kwargs.get('instance')
            db = LatexUser.objects.get(user=user)

        except Exception as e:
            db = None


    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()
            dp, created= LatexUser.objects.get_or_create(user=user)
            dp.user = user
            dp.latex_name = self.cleaned_data['latex_name']
            dp.latex_affiliation = self.cleaned_data['latex_affiliation']
            dp.save()
        return user


class ApproveUserForm(CustomUserCreationForm):
    """
    Form for handling user registration approval requests.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password1')
        self.fields.pop('password2')

    def save(self, commit=True):
        # NOTE: The superclass call is specifically to forms.ModelForm rather than CustomUserCreationForm--
        # this is done because the form doubles as an update form, and it bypasses any password checks.
        user = super(forms.ModelForm, self).save(commit=False)
        user.is_active = True
        if commit:
            user.save()
            self.save_m2m()

        return user


class ApprovalAuthenticationForm(AuthenticationForm):
    """
    Form that replaces the default Django AuthenticationForm and renders an appropriate message if an inactive user
    attempts to log in.
    """
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                ('Your registration is currently pending administrator approval.'),
                code='inactive'
            )

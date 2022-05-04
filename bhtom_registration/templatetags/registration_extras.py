from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('bhtom_registration/partials/register_button.html')
def registration_button():
    """
    Renders a register button that navigates the user to the registration form.
    """
    return


@register.inclusion_tag('bhtom_registration/partials/pending_users.html', takes_context=True)
def pending_users(context: dict) -> dict:
    """
    Renders a table of pending (AKA inactive) users with buttons to approve or delete the user.
    """
    return {
        'request': context['request'],
        'users': User.objects.filter(is_active=False)
    }

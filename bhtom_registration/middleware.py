from django.shortcuts import redirect
from django.urls import reverse
from .models import LatexUser
from bhtom2.utils.bhtom_logger import BHTOMLogger

logger: BHTOMLogger = BHTOMLogger(__name__, 'Bhtom: bhtom_registration middleware')

class RedirectAuthenticatedUsersFromRegisterMiddleware:
    """
    Middleware used to redirect authenticated users away from the register page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path_info == reverse('registration:register'):
            return redirect(reverse('user-update', kwargs={'pk': request.user.id}))

        return self.get_response(request)


class TermsCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        try:
            user_info, created = LatexUser.objects.get_or_create(user=request.user)
            if created:
                logger.info(f"Created new LatexUser profile for user {request.user.id}")
        except Exception as e:
            logger.error(f"Error retrieving or creating LatexUser for {request.user.id}: {e}")

        if not user_info.accepted_terms and request.path != "/terms/":
            return redirect("/terms/")

        return self.get_response(request)
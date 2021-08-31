from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.models import SocialApp, SocialAccount
from django.conf import settings


class Auth0LogoutAdapter(DefaultAccountAdapter):
    def get_logout_redirect_url(self, request):
        if (
            request.user.is_authenticated
            and SocialAccount.objects.filter(
                provider="auth0", user=request.user
            ).exists()
        ):
            app = SocialApp.objects.get(provider="auth0")
            query = {"client_id": app.client_id}
            if settings.AUTH0_LOGOUT_RETURN_TO:
                query["returnTo"] = settings.AUTH0_LOGOUT_RETURN_TO
            query_str = urlencode(query)
            return f"https://{settings.AUTH0_LOGIN_DOMAIN}/v2/logout/?{query_str}"
        return super().get_logout_redirect_url(request)

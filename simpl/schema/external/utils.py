from functools import wraps
from typing import TYPE_CHECKING, List

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphql.execution.base import ResolveInfo
from simpl import models

from auth0.v3.exceptions import Auth0Error

from . import auth0

User = get_user_model()

if TYPE_CHECKING:

    class UserWithAuth0(User):
        auth0_id: str


def get_auth0_ids(*users: List[User]) -> List[str]:
    return list(
        SocialAccount.objects.filter(provider="auth0", user__in=users).values_list(
            "uid", flat=True
        )
    )


def only_auth0_users(users):
    """
    Filter the queryset to only those who are auth0 users.
    """
    auth0_users = SocialAccount.objects.filter(provider="auth0", user__in=users)
    return users.filter(user__in=auth0_users)


def _get_user_data(auth0_id: str):
    try:
        return auth0.get_user_data(auth0_id)
    except Auth0Error:
        raise ValueError("Auth0 ID is not valid.")


def get_auth0_users(
    *auth0_ids: List[str], create_users: bool = True, update_user_data: bool = True
):
    users: List[UserWithAuth0] = []
    for auth0_id in auth0_ids:
        try:
            social_acct = SocialAccount.objects.get(provider="auth0", uid=auth0_id)
            if update_user_data:
                user_data = _get_user_data(auth0_id)
                if social_acct.extra_data != user_data:
                    # If user_data["email"] changed, should the user's email be changed?
                    social_acct.extra_data = user_data
                    social_acct.save()
        except SocialAccount.DoesNotExist:
            user_data = _get_user_data(auth0_id)
            email = user_data["email"]
            try:
                user = User._default_manager.get(email=email)
            except User.DoesNotExist:
                if not create_users:
                    continue
                user = User._default_manager.create(username=email, email=email)
            social_acct = SocialAccount.objects.create(
                provider="auth0", uid=auth0_id, extra_data=user_data, user=user
            )
        user = social_acct.user
        user.auth0_id = auth0_id
        users.append(user)
    return users


def simpl_token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = next(arg for arg in args if isinstance(arg, ResolveInfo)).context
        if not hasattr(context, "user") or not context.user.is_superuser:
            try:
                http_token = context.META["HTTP_AUTHORIZATION"]
                token = models.APIToken.objects.get(token=http_token)
            except (models.APIToken.DoesNotExist, KeyError):
                return None
            today = timezone.now().today()
            if token.last_used != today:
                token.last_used = today
                token.save()
        return func(*args, **kwargs)

    return wrapper

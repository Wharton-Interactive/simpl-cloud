from functools import wraps
from typing import TYPE_CHECKING, List

from allauth.socialaccount.models import SocialAccount
from auth0.v3.exceptions import Auth0Error
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphql.execution.base import ResolveInfo
from graphql.language.ast import FragmentSpread

from simpl import models

from . import auth0

User = get_user_model()

if TYPE_CHECKING:

    class UserWithAuth0(User):
        auth0_id: str


def get_auth0_ids(*users: User) -> List[str]:
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
    *auth0_ids: str, create_users: bool = True, update_user_data: bool = True
):
    users: List[UserWithAuth0] = []
    for auth0_id in auth0_ids:
        try:
            social_acct = SocialAccount.objects.get(provider="auth0", uid=auth0_id)
            if update_user_data:
                user_data = _get_user_data(auth0_id)
                if social_acct.extra_data != user_data:
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
        user: UserWithAuth0 = social_acct.user
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


def walk_fields(info):
    """
    Walk all fields in the current info ast.
    """

    def walk(fields):
        for field in fields:
            yield field
            if isinstance(field, FragmentSpread):
                selection_set = info.fragments[field.name.value].selection_set
            else:
                selection_set = field.selection_set
            if selection_set:
                yield from walk(selection_set.selections)

    return walk(info.field_asts)


def has_field_named(info, *field_names):
    """
    Return true if any fields in the schema match the name(s) provided.

    Use underscored field names and it will look for camelCase versions
    of those fields too.
    """
    assert (
        field_names
    ), "At least one field name is required (remember the first argument should be `info`)."
    all_fields = {*field_names}
    for name in field_names:
        if "_" in name:
            parts = name.split("_")
            camel_name = parts[0] + "".join(
                f"{p[:1].upper()}{p[1:]}" for p in parts[1:]
            )
            all_fields.add(camel_name)
    for field in walk_fields(info):
        if not hasattr(field, "name"):
            continue
        if field.name.value in all_fields:
            return True
    return False

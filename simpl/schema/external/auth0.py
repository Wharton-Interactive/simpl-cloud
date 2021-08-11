import sys
from typing import List
if sys.version_info >= (3, 8):
    from typing import List, TypedDict
else:
    from typing_extensions import TypedDict
from auth0.v3.management import Users, UsersByEmail
from django.conf import settings


class UserData(TypedDict):
    user_id: str
    email: str
    email_verified: bool
    username: str
    phone_number: str
    phone_verified: bool
    created_at: str
    updated_at: str
    identities: List[dict]
    app_metadata: dict
    user_metadata: dict
    picture: str
    name: str
    nickname: str
    multifactor: List[str]
    last_ip: str
    last_login: str
    logins_count: int
    blocked: bool
    given_name: str
    family_name: str


def get_access_token() -> str:
    from auth0.v3.authentication import GetToken

    non_interactive_client_id = settings.AUTH0_M2M_CLIENT_ID
    non_interactive_client_secret = settings.AUTH0_M2M_INTERACTIVE_CLIENT_SECRET
    get_token = GetToken(settings.AUTH0_M2M_DOMAIN)
    token = get_token.client_credentials(
        non_interactive_client_id,
        non_interactive_client_secret,
        "https://{}/api/v2/".format(settings.AUTH0_M2M_DOMAIN),
    )
    return token["access_token"]


def get_user_data(user_id: str) -> UserData:
    user = Users(settings.AUTH0_M2M_DOMAIN, get_access_token())
    return user.get(user_id)


def lookup_by_email(email: str) -> List[UserData]:
    search = UsersByEmail(settings.AUTH0_M2M_DOMAIN, get_access_token())
    return search.search_users_by_email(email)

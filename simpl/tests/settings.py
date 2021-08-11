SECRET_KEY = "-"

INSTALLED_APPS = [
    "simpl.apps.SimplConfig",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.auth0",
]

SIMPL_GAME_EXPERIENCE = "simpl.GameExperience"
SIMPL_RUN = "simpl.Run"
SIMPL_INSTANCE = "simpl.Instance"
SIMPL_CHARACTER = "simpl.Character"
SIMPL_PLAYER = "simpl.Player"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.postgresql", "NAME": "simpl-test"}
}

ROOT_URLCONF = "simpl.urls"

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

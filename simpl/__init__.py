from __future__ import annotations

from typing import TYPE_CHECKING, Type, Union
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from simpl.conf import settings

if TYPE_CHECKING:
    from simpl import models


def _get_model(key: str):
    model = getattr(settings, f"SIMPL_{key}")
    try:
        return django_apps.get_model(model, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            f"SIMPL_{key} must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            f"SIMPL_{key} refers to model '{model}' that has not been installed"
        )


def get_character_model() -> Type[
    Union[models.BaseCharacterData, models.BaseCharacterLinked]
]:
    return _get_model("CHARACTER")


def get_game_experience_model() -> Type[models.BaseGameExperience]:
    return _get_model("GAME_EXPERIENCE")


def get_instance_model() -> Type[models.BaseInstance]:
    return _get_model("INSTANCE")


def get_player_model() -> Type[models.BasePlayer]:
    return _get_model("PLAYER")


def get_run_model() -> Type[models.BaseRun]:
    return _get_model("RUN")

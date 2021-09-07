from __future__ import annotations

from typing import TYPE_CHECKING, List, Union


if TYPE_CHECKING:
    from .models import BasePlayer
    from allauth.socialaccount.models import SocialAccount


UNSET = object()


def start_continuous_singleplayer(instance: BasePlayer, **kwargs):
    if (
        not instance.character
        and instance.user
        and not instance.inactive
        and instance.ready
        and instance.run.continuous_open
    ):
        simpl_instance = instance.run.create_singleplayer_instance(instance)
        instance.run.start_instances([simpl_instance])


def update_user_from_socialaccount(instance: SocialAccount, **kwargs):
    data = instance.extra_data
    if not instance.user or not instance.extra_data:
        return

    def _update_user(
        key: str, data_key: Union[str, List[str]] = None, *, only_if_empty: bool = False
    ):
        user_value = getattr(instance.user, key)
        if only_if_empty and user_value:
            return False
        value = None
        if data_key is None:
            data_keys = [key]
        elif isinstance(data_key, str):
            data_keys = [data_key]
        else:
            data_keys = data_key
        for data_key in data_keys:
            value = data.get(data_key, UNSET)
            if value:
                break
        if value is UNSET or value == user_value:
            return False
        setattr(instance.user, key, value)
        return True

    changed = False
    changed |= _update_user("email", only_if_empty=True)
    changed |= _update_user("first_name", ["given_name", "first_name"])
    changed |= _update_user("last_name", ["family_name", "last_name"])

    if changed:
        instance.user.save()

from __future__ import annotations

import dataclasses
import enum
from typing import NewType, Dict

from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.module_loading import import_string

from simpl.models import Run


class NavStatus(enum.Enum):
    DISABLED = 0
    UNSTARTED = 1
    INCOMPLETE = 2
    READY = 3
    COMPLETE = 4


@dataclasses.dataclass(frozen=True)
class NavItem:
    name: str
    status: NavStatus = NavStatus.UNSTARTED
    hint: str = ""
    url: str = None
    next_url: str = None
    hidden: bool = False


NavType = NewType("NavType", Dict[str, NavItem])


def change_item(data: NavType, key: str, **kwargs):
    data[key] = dataclasses.replace(data[key], **kwargs)


def is_configuring(run: Run):
    return run.status in (Run.STATUS.SETUP, Run.STATUS.PREPARE)


def _add_urls(data: NavType, run: Run):
    data = dict(data)
    next_url = None
    for key, item in reversed(list(data.items())):
        try:
            url = reverse(f"simpl.{key}", kwargs={"pk": run.pk})
        except NoReverseMatch:
            url = None
        change_item(data, key, url=url, next_url=next_url)
        if item.status != NavStatus.DISABLED:
            next_url = url
    return data


def _get_and_order_nav_data(func_str: str, run: Run):
    data: NavType = dict(import_string(func_str)(run))
    # TODO: order
    return data


def get_setup(run: Run):
    data = _get_and_order_nav_data(settings.SIMPL_SETUP_NAV, run)
    return _add_urls(data, run)


def get_play(run: Run):
    data = _get_and_order_nav_data(settings.SIMPL_PLAY_NAV, run)
    return _add_urls(data, run)


def get_nav(run: Run):
    nav_func = get_setup if is_configuring(run) else get_play
    return nav_func(run)


def get_next_item(run: Run, current_name: str):
    available_items = dict(
        (key, item)
        for key, item in get_nav(run).items()
        if item.status != NavStatus.DISABLED and item.url
    )
    item_names = list(available_items)
    next_name = None
    try:
        current_index = item_names.index(current_name)
    except ValueError:
        # Fall back to the first available item.
        return list(available_items.values())[0]
    if current_index != -1:
        if is_configuring(run):
            # Get the next item
            try:
                next_name = item_names[current_index + 1]
                return available_items[next_name]
            except IndexError:
                pass
        return available_items[current_name]


def get_next_url(run: Run, current_name: str):
    return get_next_item(run, current_name).url

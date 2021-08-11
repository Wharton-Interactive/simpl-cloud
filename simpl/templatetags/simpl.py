import math
import re

import mmh3
from django import template

register = template.Library()


def rshift(val, n):
    return (val % 0x100000000) >> n


@register.filter
def playercolor(player):
    saturation = 41
    lightness = 24
    hash = mmh3.hash(str(player), 3)
    h = hash % 360
    s = rshift(hash, 11) % 100
    el = rshift(hash, 17) % 100
    s = math.floor((s / 100) * saturation + (100 - saturation) / 2)
    el = math.floor((el / 100) * lightness + (100 - lightness) / 2.5)
    return f"hsl({h},{s}%,{el}%)"


@register.filter
def playerinitials(player):
    initials = re.sub(r"(\w)[^ ]+", r"\1", str(player))
    initials = re.sub(r"[^\w]", "", initials)
    return f"{initials[0]}{initials[-1]}"

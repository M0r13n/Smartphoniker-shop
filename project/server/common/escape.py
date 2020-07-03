"""
Escape special characters like it's 1990.
This is needed, because our old ERP system can handle Unicode -.-
"""

# These are only common names. More complex names or even different languages WILL cause problems.
from typing import Dict

SPECIAL_CHARS = {
    'ä': 'ae',
    'ü': 'ue',
    'ö': 'oe',
    'ß': 'ss'
}


def replace(old: str) -> str:
    """ Check if the char is a special char and return it's replacement"""
    if not len(old) == 1:
        raise ValueError("Expected single character and not a sequence")
    upper = old.isupper()
    replacement = SPECIAL_CHARS.get(old.lower(), None)
    if replacement:
        return replacement.title() if upper else replacement
    return old


def cleanify(string: str):
    return "".join([replace(char) for char in string])


def cleanify_dict(params: Dict):
    for k, v in params.items():
        try:
            params[k] = cleanify(v)
        except TypeError:
            continue

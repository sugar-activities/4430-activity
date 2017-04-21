#! /usr/bin/env python

import codecs
import gettext
import json

# TBD: generate $.i18n.choose_pluralized_msg. Similar to how python
# gettext does this.

def context_and_key(key):
    """Return a tuple containing the context (or None) and the message
    key."""
    # A context, if present, is prepended to the key, with a \x04
    # character in between.
    (context, separator, k) = key.partition(u'\x04')
    if (separator != ''):
        return (context, k)
    else:
        return (None, key)

def group_pluralized_forms(dict):
    """Return a dictionary where the pluralized forms from dict are
    grouped. Elements of the form
    (msg, i) -> tr1
    ...
    (msg, j) -> trn
    are grouped into:
    msg -> [tr1, ..., trn]
    """
    result = {}
    keys = dict.keys()
    keys.sort()
    for k in keys:
        translation = dict[k]
        if type(k) is tuple:
            # A pluralized form k = (msg, n)
            k = k[0]
            if k not in result:
                result[k] = []
            result[k].append(translation)
        else:
            result[k] = translation
    return result

def path(key):
    """Return the path in the dictionary for key"""
    (context, key) = context_and_key(key)
    if context is not None:
        return ['contextualized_strings', context, key]
    else:
        return ['strings', key]

def store_translation(dictionary, key, translation):
    p = path(key)
    while len(p) > 1:
        x = p.pop(0)
        dictionary = dictionary.setdefault(x, {})
    dictionary[p[0]] = translation

def gettext_json(fp, indent = False):
    result = {}
    tr = gettext.GNUTranslations(fp)
    dictionary = group_pluralized_forms(tr._catalog)
    for k, v in group_pluralized_forms(tr._catalog).items():
        store_translation(result, k, v)
    return json.dumps(result, ensure_ascii = False, indent = indent)

import tracery
import tracery.modifiers
import json
import re


def once(text, *params, used=set()):
    m = re.search(r"<([^>]+)>", text)
    if m is None:
        return text
    tag = m.group(0)
    if tag in used:
        return ""
    else:
        used.add(tag)
        return re.sub(r"<[^>]+>", "", text)


rules = json.load(open("grammar.json"))
grammar = tracery.Grammar(rules)
grammar.add_modifiers(tracery.modifiers.base_english)
grammar.add_modifiers({"once": once})


def const(value):
    def f(*args, **kwargs):
        return value

    return f


def lookup(key, **kwargs):
    for k, v in kwargs.items():
        if isinstance(v, str):
            v = const(v)
        grammar.add_modifiers({k: v})
    return grammar.flatten("#" + key + "#")


flatten = grammar.flatten

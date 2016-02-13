#!/usr/bin/python


def pretty_print(string, colour="", decoration=""):
    s = ""
    if decoration != "":
        s += decoration
    if colour != "":
        s += colour
    s += string
    if colour != "" or decoration != "":
        s += TextDecorations.END_DECORATION
    print(s)


class TextDecorations:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END_DECORATION = '\033[0m'

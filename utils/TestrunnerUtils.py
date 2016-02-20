#!/usr/bin/python


def clean_raw_telnet(telnet_output):
    # Recreate output based on newline symbols, removing blank lines
    split_str = "".join(telnet_output).split("\r\n")
    while split_str.count("") > 0:
        split_str.remove("")
    return split_str


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

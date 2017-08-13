#!/usr/bin/python

import re

regex1 = re.compile('\S+ Optional<[^>]+>\n. - some : "(.*)"\n$')
regex2 = re.compile(' *"(.*)"\n$')

def strip (str): 
    match = regex1.match(str)
    if match :
        return match.group(1)
    match = regex2.match(str)
    if match :
        return match.group(1)
    return str


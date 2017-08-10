#!/usr/bin/python

import re

aaa_regex1 = re.compile('\S+ Optional<[^>]+>\n. - some : "(.*)"\n$')
aaa_regex2 = re.compile(' *"(.*)"\n$')

def strip (str): 
    m = aaa_regex1.match(str)
    if m : 
        return m.group(1)
    m = aaa_regex2.match(str)
    if m : 
        return m.group(1)
    return str


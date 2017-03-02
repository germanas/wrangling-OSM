#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        k = element.get("k")
        l = re.search(lower,k)
        lc = re.search(lower_colon,k)
        pc = re.search(problemchars,k)
        if l:
            print l.group()
            keys['lower'] +=1
        elif lc:
            print lc.group()
            keys['lower_colon'] +=1
        elif pc:
            print pc.group()
            keys['problemchars'] +=1
        else:
            keys['other'] +=1
            pprint.pprint(keys['other'])
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



pprint.pprint(process_map('vilniusmap.osm'))
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re

good_postcodes = re.compile(r'(LT[\-\s]\d{5})')
bad_postcodes = re.compile(r'(^[0-9]{5}$)')

#Check for problem with postcodes
def check_postcode(element, keys):
    if element.tag == "tag":
        v = element.get("v")
        l = re.search(good_postcodes, v)
        d = re.search(bad_postcodes, v)
        if l:
            print l.group()
            keys['Good'] +=1
        elif d:
            print d.group()
            keys['Bad'] +=1
        else:
            keys['Irrelevant'] +=1
    return keys

#Iterates through the file.
def process_map(filename):
    keys = {"Good": 0, "Bad": 0, "Irrelevant" :0}
    for _, element in ET.iterparse(filename):
        keys = check_postcode(element, keys)

    return keys

pprint.pprint(process_map('vilniusmap.osm'))
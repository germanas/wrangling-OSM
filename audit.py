#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "vilniusmap.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) #Checks if the value has a street type


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]


#This function checks if the type of street name matches the ones in the expected list. If it doesn't then it adds to new list
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


#This function checks if the key attribute contains value with colon
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#This function iterates through the file and checks for nodes and way tags.
def audit(osmfile):
    with open(osmfile, "r") as osm_file:
        street_types = defaultdict(set)
        for event, elem in ET.iterparse(osm_file, events=("start",)):

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types , tag.attrib['v'])

        return street_types



def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))


test()
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "vilniussample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["gatve", "aikste", "aleja"]

# UPDATE THIS VARIABLE
mapping = { "g.": "gatve",
            "a.": "aikste",
            "al.": "aleja"
                      }

 
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)



def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    with open(osmfile, "r") as osm_file:
        street_types = defaultdict(set)
        #street_types = audit(osmfile)
        for event, elem in ET.iterparse(osm_file, events=("start",)):

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])

        return street_types


def update_name(name, mapping):
    
        m = street_type_re.search(name)
        if m not in expected:
            name = re.sub(m.group(), mapping[m.group()], name)

        return name


def test():
    st_types = audit(OSMFILE)
    pprint.pprint(st_types)


test()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
 
import cerberus
 
import schema
 
OSM_PATH = "vilniusmap.osm"

#These are the locations my csv files will be stored in
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

#Created regex variables to match my values to
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
FIND_GATVE = re.compile(r'(.*?)\sg\.$')
FIND_ALEJA = re.compile(r'(.*?)\s\bal\b.$')
FIND_AIKSTE = re.compile(r'(.*?)\sa\.$')
FIND_AKLIGATVIS = re.compile(r'(.*?)\s\baklg\b.$')
FIND_KELIAS = re.compile(r'(.*?)\s\bkel\b.$')
FIND_PLENTAS = re.compile(r'(.*?)\s\bpl\b.$')
FIND_PROSPEKTAS = re.compile(r'(.*?)\s\bpr\b.$')
FIND_SKERSGATVIS = re.compile(r'(.*?)\s\bskg\b.$')
 
SCHEMA = schema.schema
 
# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
 
 
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
        for child in element:
            node_tag = {}
            if LOWER_COLON.match(child.attrib['k']): #Checks if the child attribute "key" matches the regex.
                node_tag['type'] = child.attrib['k'].split(':',1)[0]
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = fix_streets(child.attrib['v']) #References helper function that fixes streets
                tags.append(node_tag)
            elif PROBLEMCHARS.match(child.attrib['k']): #If there are problemchars in the child attribute, then skip it.
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = fix_streets(child.attrib['v'])
                tags.append(node_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        position = 0
        for child in element:
            way_tag = {}
            way_node = {}
            if child.tag == 'tag':
                if LOWER_COLON.match(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = fix_streets(child.attrib['v'])
                    print way_tag['value'] #Checking if it works
                    tags.append(way_tag)
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = fix_streets(child.attrib['v'])
                    tags.append(way_tag)
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    print tags
 
 
# ================================================== #
#               Helper Functions                     #
# ================================================== #
#This function takes an attribute of a node, of way, then checks it against RegEx and if it matches, it will replace the words.
def fix_streets(attribute):
    if FIND_GATVE.match(attribute):
        return attribute.replace('g.', 'gatvė'.decode("utf-8"))
    elif FIND_ALEJA.match(attribute):
        return attribute.replace('al.', 'alėja'.decode("utf-8"))
    elif FIND_AIKSTE.match(attribute):
        return attribute.replace('a.', 'aikštė'.decode("utf-8"))
    elif FIND_AKLIGATVIS.match(attribute):
        return attribute.replace('aklg.', 'akligatvis')
    elif FIND_KELIAS.match(attribute):
        return attribute.replace('kel.', 'kelias')
    elif FIND_PLENTAS.match(attribute):
        return attribute.replace('pl.', 'plentas')
    elif FIND_PROSPEKTAS.match(attribute):
        return attribute.replace('pr.', 'prospektas')
    elif FIND_SKERSGATVIS.match(attribute):
        return attribute.replace('skg.', 'skersgatvis')
    else:
        return attribute

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
 
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
 
 
def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
       
        raise Exception(message_string.format(field, error_string))
 
 
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""
 
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })
 
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
 
 
# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:
 
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
 
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
 
        validator = cerberus.Validator()
 
        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)
 
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
 
 
if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
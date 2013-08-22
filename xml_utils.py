#!/usr/bin/env python

import xml.etree.cElementTree as ET

__author__ = 'akurilin'


def add_elements(dic, parent=None):
    if parent is None:
        element = ET.Element(dic["name"])
    else:
        element = ET.SubElement(parent, dic["name"])
    if "attrib" in dic:
        for key in dic["attrib"].keys():
            element.set(key, dic["attrib"][key])
    if "text" in dic:
        element.text = dic["text"]
    if "child" in dic:
        for child in dic["child"]:
            add_elements(child, element)
    return element


def xml_to_string(root_elem):
    return ET.tostring(root_elem)
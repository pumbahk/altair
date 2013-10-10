# -*- coding:utf-8 -*-


import re

IMPORT_RX = re.compile(r'@import *(.+?);')
URL_RX = re.compile(r'url\((.+?)\)')

def css_url_iterator(io):
    """more looser than cssutils.replaceUrls"""
    for line in io:
        m = URL_RX.search(line)
        if m:
            yield m.group(1).strip("'").strip('"')
        m = IMPORT_RX.search(line)
        if m:
            yield m.group(1).strip("'").strip('"')

def abspath_from_rel(rel, cwd):
    if rel.startswith("/"):
        raise ValueError("not relative path: {}".format(rel))

    nodes = rel.split("/")
    if not nodes:
        return cwd
    if nodes[0] == "./":
        nodes.pop(0)

    cwd_nodes = cwd.split("/")
    while nodes[0] == "..":
        nodes.pop(0)
        cwd_nodes.pop(-1)
    return "{}/{}".format("/".join(cwd_nodes).rstrip("/"), ("/").join(nodes).lstrip("/"))

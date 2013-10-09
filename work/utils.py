# -*- coding:utf-8 -*-
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

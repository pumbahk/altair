# -*- coding:utf-8 -*-
import os
from altaircms.helpers import url_create_with
from markupsafe import Markup

class StaticPageDirectoryRenderer(object):
    def __init__(self, request, static_page, static_directory):
        self.request = request
        self.page = static_page
        self.pageset = static_page.pageset
        self.static_directory = static_directory
        self.basedir = static_directory.get_base_directory()
        if not self.basedir.endswith("/"):
            self.basedir += "/"

    def __html__(self):
        self.root = self.static_directory.get_rootname(self.page)
        return TreeRenderer(self.request, self.root, self).__html__()

    def create_url(self, path):
        return self.request.route_path("static_page_display",  path=path.replace(self.basedir, "")).replace("%2F", "/")

    def has_children(self, path):
        return os.path.isdir(path)

    def get_children(self, path):
        return (f for f in  os.listdir(path) if not f.endswith(".original"))

    def join_name(self, dirname, path):
        return os.path.join(dirname, path)

    def parent_action_links(self, path):
#         part = path.replace(self.root, "")
#         return u'''
# <a class="btn btn-mini" href="{0}">新しいファイルを追加</a>
# <a class="btn btn-mini" href="{1}"><i class="icon-trash">_</i>削除</a>
# '''.format(self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="create"), 
#            self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="delete"))
        return u""

class TreeRenderer(object):
    def __init__(self, request, root, companion):
        self.request = request
        self.root = root
        self.companion = companion

    def create_url(self, path):
        url = self.companion.create_url(path)
        if self.request.GET:
            return url_create_with(url, **self.request.GET)
        else:
            return url

    def parent_action_links(self, path, r):
        r.append(self.companion.parent_action_links(path))

    def _url_tree(self, path, r, opened=False):
        if self.companion.has_children(path):
            r.append(u'<ul>')
            id_ = path.replace(self.root, "").replace("/", "-")
            if opened:
                r.append(u'<li><input type="checkbox" checked="checked" id="{0}"/><label for="{0}">{1}</label>'.format(id_, os.path.basename(path)))
            else:
                r.append(u'<li><input type="checkbox" id="{0}"/><label for="{0}">{1}</label>'.format(id_, os.path.basename(path)))
            self.parent_action_links(path, r)
            r.append(u'<ul>')
            for subpath in self.companion.get_children(path):
                self._url_tree(self.companion.join_name(path, subpath), r, opened=False)
            r.append(u'</ul>')
            r.append(u'</li></ul>')
        else:
            r.append(u'<li>')
            r.append(u'<a href="%s">%s</a>' % (self.create_url(path), os.path.basename(path)))            
            r.append(u'</li>')
        return r

    def __html__(self):
        r = self._url_tree(self.root, [], opened=True)
        return Markup(u'\n'.join(r))

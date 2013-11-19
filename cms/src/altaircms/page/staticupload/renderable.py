# -*- coding:utf-8 -*-
import os
from altaircms.helpers import url_create_with
from markupsafe import Markup

def static_page_directory_renderer(request, static_page, static_directory, management=False):
    if static_page.uploaded_at:
        return StaticPageDirectoryRendererFromDB(request, static_page, static_directory, management=management)
    else:
        return StaticPageDirectoryRenderer(request, static_page, static_directory, management=management)

## helper structure
class _Node(object):
    def __init__(self, root, D):
        self.root = root
        self.children = {}
        self.D = D
        D[root] = self
    
    @classmethod
    def create_from_dict(cls, D, prefix=""):
        nodes = [k.split("/") for k in D.keys()]
        mem = {}
        root = cls(prefix, mem)
        for n in nodes:
            root._add_element(n)
        return root

    def _add_element(self, n):
        if isinstance(n,(tuple, list)) and n:
            if not self.children.get(n[0]):
                fullname = u"{0}/{1}".format(self.root, n[0]) if self.root else n[0]
                self.children[n[0]] = _Node(fullname, self.D)
            self.children[n[0]]._add_element(n[1:])


class StaticPageDirectoryRendererFromDB(object):
    def __init__(self, request, static_page, static_directory, management=False):
        self.request = request
        self.page = static_page
        self.pageset = static_page.pageset
        self.static_directory = static_directory
        self.node = _Node.create_from_dict(static_page.file_structure, prefix=unicode(static_page.id))
        self.management = management
        self.rendered = {}

    def preview_url(self, path):
        return self.request.route_path("static_page_display", 
                                       static_page_id=self.pageset.id, 
                                       child_id=self.page.id, 
                                       path=u"{0}/{1}".format(self.pageset.hash, path)).replace("%2F", "/")

    def delete_file_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="delete", 
                                       _query=dict(endpoint=self.request.url))
    def update_file_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="update", 
                                       _query=dict(endpoint=self.request.url))

    def delete_directory_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="delete", 
                                       _query=dict(endpoint=self.request.url))

    def has_children(self, path):
        return path.endswith("$") or bool(self.node.D[path].children)

    def unregistered_parent(self, path):
        return not path.rstrip("$") in self.rendered

    def register_parent(self, path):
        path = path.rstrip("$")
        self.rendered[path] = 1
        return path

    def get_children(self, path):
        try:
            return (f for f in  self.node.D[path].children.keys() if not f.endswith(".original"))
        except KeyError:
            return []

    def join_name(self, dirname, basename):
        return u"{0}/{1}".format(dirname, basename)

    def parent_action_links(self, path):
        part = path.replace(self.root, "")
        return u'''
<a class="btn btn-mini" href="{0}">新しいディレクトリを追加</a></li>
<a class="btn btn-mini" href="{1}">新しいファイルを追加</a></li>
<a class="btn btn-mini" href="{2}">削除<i class="icon-trash"></i></a>           
'''.format(self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="create", 
                                   _query=dict(endpoint=self.request.url)), 
           self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="create", 
                                   _query=dict(endpoint=self.request.url)), 
           self.delete_directory_url(path))

    def __html__(self):
        self.root = unicode(self.page.id)
        return TreeRenderer(self.request, self.root, self).__html__()

class StaticPageDirectoryRenderer(object):
    def __init__(self, request, static_page, static_directory, management=False):
        self.request = request
        self.page = static_page
        self.pageset = static_page.pageset
        self.static_directory = static_directory
        self.basedir = static_directory.get_base_directory()
        if not self.basedir.endswith("/"):
            self.basedir += "/"
        self.management = management
        self.rendered = {}

    def preview_url(self, path):
        part = path.replace(self.basedir, "").replace("%2F", "/")
        return self.request.route_path("static_page_display", static_page_id=self.pageset.id, child_id=self.page.id, path=part)
    
    def delete_file_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="delete", 
                                       _query=dict(endpoint=self.request.url))
    def update_file_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="update", 
                                       _query=dict(endpoint=self.request.url))

    def delete_directory_url(self, path):
        part = path.replace(self.root, "")
        return self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="delete", 
                                       _query=dict(endpoint=self.request.url))

    def has_children(self, path):
        return os.path.isdir(path)

    def get_children(self, path):
        files = []
        for f in  os.listdir(path):
            if not f.endswith(".original"):
                if not "." in f:
                    yield f
                else:
                    files.append(f)
        for f in files:
            yield f

    def join_name(self, dirname, path):
        return os.path.join(dirname, path)

    def parent_action_links(self, path):
        part = path.replace(self.root, "")
        return u'''
<a class="btn btn-mini" href="{0}">新しいディレクトリを追加</a></li>
<a class="btn btn-mini" href="{1}">新しいファイルを追加</a></li>
<a class="btn btn-mini" href="{2}">削除<i class="icon-trash"></i></a>           
'''.format(self.request.route_path("static_page_part_directory", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="create", 
                                   _query=dict(endpoint=self.request.url)), 
           self.request.route_path("static_page_part_file", static_page_id=self.pageset.id, child_id=self.page.id, path=part, action="create", 
                                   _query=dict(endpoint=self.request.url)), 
           self.delete_directory_url(path))
    
    def unregistered_parent(self, path):
        return not path in self.rendered

    def register_parent(self, path):
        self.rendered[path] = 1
        return path

    def __html__(self):
        self.root = self.static_directory.get_rootname(self.page)
        return TreeRenderer(self.request, self.root, self).__html__()

class TreeRenderer(object):
    def __init__(self, request, root, companion):
        self.request = request
        self.root = root
        self.companion = companion

    def normalize_url(self, url):
        if self.request.GET:
            return url_create_with(url, **self.request.GET)
        else:
            return url

    def parent_action_links(self, path, r):
        r.append(self.companion.parent_action_links(path))

    def _url_tree(self, path, r, opened=False):
        if self.companion.has_children(path):
            if not self.companion.unregistered_parent(path):
                return r
            path = self.companion.register_parent(path)
            r.append(u'<ul>')
            id_ = path.replace(self.root, "").replace("/", "-")
            if opened:
                r.append(u'<li><input type="checkbox" checked="checked" id="{0}"/><label for="{0}">{1}</label>'.format(id_, os.path.basename(path)))
            else:
                r.append(u'<li><input type="checkbox" id="{0}"/><label for="{0}">{1}</label>'.format(id_, os.path.basename(path)))
            r.append(u'<ul>')
            for subpath in self.companion.get_children(path):
                self._url_tree(self.companion.join_name(path, subpath), r, opened=False)
            if self.companion.management:
                self.parent_action_links(path, r)
            r.append(u'</ul>')
            r.append(u'</li></ul>')
        else:
            r.append(u'<li>')
            r.append(u'<a href="%s">%s</a>' % (self.normalize_url(self.companion.preview_url(path)), os.path.basename(path)))            
            if self.companion.management:
                r.append(u'<a href="%s"><i class="icon-cog"></i>%s</a>' % (self.normalize_url(self.companion.update_file_url(path)), u""))            
                r.append(u'<a href="%s"><i class="icon-trash"></i>%s</a>' % (self.normalize_url(self.companion.delete_file_url(path)), u""))            
            r.append(u'</li>')
        return r

    def __html__(self):
        r = self._url_tree(self.root, [], opened=True)
        return Markup(u'\n'.join(r))

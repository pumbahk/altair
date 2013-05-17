import os
from altaircms.helpers import url_create_with
from markupsafe import Markup

class StaticPageDirectoryRenderer(object):
    def __init__(self, request, static_page, static_directory):
        self.request = request
        self.static_page = static_page
        self.static_directory = static_directory
        self.basedir = static_directory.get_base_directory()
        if not self.basedir.endswith("/"):
            self.basedir += "/"

    def __html__(self):
        root = self.static_directory.get_rootname(self.static_page)
        return TreeRenderer(self.request, root, self).__html__()

    def create_url(self, path):
        return self.request.route_path("static_page_display",  path=path.replace(self.basedir, "")).replace("%2F", "/")

    def has_children(self, path):
        return os.path.isdir(path)

    def get_children(self, path):
        return os.listdir(path)

    def join_name(self, dirname, path):
        return os.path.join(dirname, path)

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

    def _url_tree(self, path, r):
        if self.companion.has_children(path):
            r.append(u"<li>%s</li>" % os.path.basename(path))
            r.append(u"<ul>")
            for subpath in self.companion.get_children(path):
                self._url_tree(self.companion.join_name(path, subpath), r)
            r.append(u"</ul>")
        else:
            r.append(u"<li>")
            r.append(u'<a href="%s">%s</a>' % (self.create_url(path), os.path.basename(path)))            
            r.append(u"</li>")
        return r

    def __html__(self):
        r = self._url_tree(self.root, [])
        return Markup(u"\n".join(r))

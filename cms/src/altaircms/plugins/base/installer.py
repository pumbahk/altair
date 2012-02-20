import os
import filecmp
from pyramid.asset import abspath_from_asset_spec

class PluginInstallExceptioni(Exception):
    pass

class _FileLinker(object):
    def __init__(self, force=False):
        self.force = force

    def has_file(self, path):
        return os.path.exists(path)

    def is_valid_link(self, src, dst):
        return os.path.isfile(dst) and  filecmp.cmp(src, dst)

    def _after_invalid(self, dst):
        if self.force:
            os.remove(dst)
        else:
            raise PluginInstallExceptioni("%s file is found. but this is invalid." % dst)

    def _make_dir_if_need(self, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def make_link_if_need(self, src, dst):
        src = os.path.abspath(src)
        self._make_dir_if_need(os.path.dirname(dst))

        if self.has_file(dst):
            if self.is_valid_link(src, dst):
                return
            self._after_invalid(dst)
        os.symlink(src, dst)

def _translate_path(dst, plugin_name, filename, file_type, path):
    """
    >>> _translate_path("app:static", "widget", "image", "js", "api.js")
    'app:static/js/widget/api/image.js'

    >>> _translate_path("app:static", "widget", "image", "js", "foo/bar/api.js")
    'app:static/js/widget/api/image.js'
    """
    base, ext = os.path.splitext(path)
    base = os.path.basename(base)
    return os.path.join(dst, file_type, plugin_name, base, filename)+ext

class BasePluginInstaller(object):
    PLUGIN_KEY = "altaircms_plugin_store"
    plugin_type = "base"

    def __init__(self, pyramid_settings):
        self.pyramid_settings = pyramid_settings
        self.linker = _FileLinker()

    def install(self, settings):
        self.settings = settings
        self.install_resource()
        self.attach_plugin_settings()

    def attach_plugin_settings(self):
        """ add plugin settings bound to Pyramid_Settings
        """
        store = self.pyramid_settings.get(self.PLUGIN_KEY)
        if store is None:
            store = {}
        plugin_settings = self.settings
        store[self.settings["name"]] = plugin_settings
        self.pyramid_settings[self.PLUGIN_KEY] = store
        
    def install_resource(self):
        dst = self.pyramid_settings.get("plugin.static_directory")
        if not dst:
            ## fixme message
            raise PluginInstallExceptioni("plugin.static_directory is not found in your pyramid_settings'")

        dst = abspath_from_asset_spec(dst)
        widget_name = self.settings["name"]

        if self.settings.get("jsfile"):
            f = self.settings.get("jsfile")
            self.linker.make_link_if_need(f, _translate_path(dst, self.plugin_type, widget_name, "js", f))
        if self.settings.get("cssfile"):
            f = self.settings.get("cssfile")
            self.linker.make_link_if_need(f, _translate_path(dst, self.plugin_type, widget_name, "css", f))


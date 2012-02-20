from altaircms.widget.fetcher import WidgetFetcher
from altaircms.plugins.base.installer import BasePluginInstaller

class WidgetPluginInstaller(BasePluginInstaller):
    plugin_type = "widget"
    def install(self, settings):
        super(WidgetPluginInstaller, self).install(settings)
        self.install_fetcher()

    def install_fetcher(self):
        model = self.settings["model"]
        widget_name = self.settings["name"]
        WidgetFetcher.add_fetch_method(widget_name, model)

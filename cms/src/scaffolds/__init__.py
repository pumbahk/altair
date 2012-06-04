from pyramid.scaffolds import PyramidTemplate

class WidgetPluginTemplate(PyramidTemplate):
    summary = "altaircms widget plugin structure"
    _template_dir = "widget"

    def pre(self, command, output_dir, vars):
        vars["Package"] = vars['package'][0].upper() + vars["package"][1:]
        return PyramidTemplate.pre(self, command, output_dir, vars)

class AssetWidgetPluginTemplate(PyramidTemplate):
    summary = "altaircms asset widget plugin structure"
    _template_dir = "asset_widget"

    def pre(self, command, output_dir, vars):
        vars["Package"] = vars['package'][0].upper() + vars["package"][1:]
        return PyramidTemplate.pre(self, command, output_dir, vars)

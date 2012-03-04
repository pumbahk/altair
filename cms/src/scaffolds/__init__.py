from paste.util.template import paste_script_template_renderer
from paste.script import templates

class WidgetPluginTemplate(templates.Template):
    summary = "altaircms widget plugin structure"
    _template_dir = "widget"
    template_renderer = staticmethod(paste_script_template_renderer)

    def pre(self, command, output_dir, vars):
        vars["Package"] = vars['package'][0].upper() + vars["package"][1:]
        return templates.Template.pre(self, command, output_dir, vars)

    

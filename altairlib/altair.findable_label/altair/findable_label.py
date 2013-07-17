from zope.interface import Interface
from zope.interface import provider

def includeme(config):
    config.add_tween(".findable_label.findable_label_tween_factory")
    output = config.maybe_dotted(config.registry.settings.get("altair.findable_label.output", ".findable_label.AppendHeaderElementOutput"))
    config.registry.registerUtility(provider(IFindableLabelOutput)(output(config)))

class IFindableLabelOutput(Interface):
    def rewrite(response):
        pass
    def output(response_body):
        pass

class AppendHeaderElementOutput(object):
    def __init__(self, config):
        self.labelname = config.registry.settings.get("altair.findable_label.label", "[unknown]").decode("utf-8")
        self.color = config.registry.settings.get("altair.findable_label.color", "#220000")
        self.background_color = config.registry.settings.get("altair.findable_label.background_color", "#ffaaaa")

    def rewrite(self, response):
        result = self.output(response.text)
        response.body = ""
        response.write(result.encode("utf-8"))
        return response

    def output(self, html):
        return html.replace(u"</body>", u"""
<div style="width:60px; height:32px; position: fixed; top:5px; left:10px; background-color: %s; color: %s; z-index: 10000;">
  %s
</div>
</body>
""" % (self.background_color, self.color, self.labelname),  1)
    

def findable_label_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        content_type = response.content_type
        if content_type and content_type.lower() in ["text/html"] and response.charset is not None:
            instance = registry.getUtility(IFindableLabelOutput)
            response = instance.rewrite(response)
        return response
    return tween


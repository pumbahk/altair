from zope.interface import Interface
from zope.interface import provider

def includeme(config):
    config.add_tween(".findable_label.findable_label_tween_factory")
    output = config.maybe_dotted(config.registry.settings.get("altair.findable_label.output", ".findable_label.AppendHeaderElementOutput"))
    labelname = config.registry.settings.get("altair.findable_label.label", "[unknown]").decode("utf-8")
    config.registry.registerUtility(provider(IFindableLabelOutput)(output(labelname)))

class IFindableLabelOutput(Interface):
    def rewrite(response):
        pass
    def output(response_body):
        pass

class AppendHeaderElementOutput(object):
    def __init__(self, labelname, description=None):
        self.labelname = labelname
        self.description = description

    def rewrite(self, response):
        result = self.output(response.text)
        response.body = ""
        response.write(result.encode("utf-8"))
        return response

    def output(self, html):
        return html.replace(u"</body>", u"""
<div style="width:20px; height:100%%; position: fixed; top:00px; left:0px; background-color: #222; color: #ccc">
  <div style="font-size:14pt; position:relative; top: 60px;">
  %s
  </div>
</div>
</body>
""" % self.labelname,  1)
    

def findable_label_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        content_type = response.content_type
        if content_type and content_type.lower() in ["text/html"]:
            instance = registry.getUtility(IFindableLabelOutput)
            response = instance.rewrite(response)
        return response
    return tween


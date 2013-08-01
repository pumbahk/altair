import sys
from zope.interface import Interface
from zope.interface import implementer

class MissingValue(Exception):
    pass

def includeme(config):
    OutputClass = config.maybe_dotted(config.registry.settings.get("altair.findable_label.output", AppendHeaderElementOutput))
    try:
        output = OutputClass.from_settings(config.registry.settings)
        config.registry.registerUtility(output, IFindableLabelOutput)
        config.add_tween("altair.findable_label.findable_label_tween_factory")
    except MissingValue as e:
        sys.stderr.write("altair.findable_label: {}".format(str(e)))

class IFindableLabelOutput(Interface):
    def rewrite(response):
        pass
    def output(response_body):
        pass

@implementer(IFindableLabelOutput)
class AppendHeaderElementOutput(object):
    def __init__(self, labelname, color, background_color):
        self.labelname = labelname
        self.color = color
        self.background_color = background_color

    @classmethod
    def from_settings(cls, settings, prefix="altair.findable_label."):
        try:
            labelname = settings[prefix+"label"].decode("utf-8")
        except KeyError:
            raise MissingValue("{prefix}label is not found in settings".format(prefix=prefix))

        color = settings.get(prefix+"color", "#220000")
        background_color = settings.get("background_color", "#ffaaaa")
        return cls(labelname, color, background_color)

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


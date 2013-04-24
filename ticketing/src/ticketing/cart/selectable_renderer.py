# encoding: utf-8
from pyramid_selectable_renderer import SelectableRendererSetup
from pyramid_selectable_renderer.custom import RecieveTemplatePathFormat, RecieveTemplatePathCandidatesDict, SelectByRequestGen

@SelectByRequestGen.generate
def get_template_path_args(request):
    from ticketing.core.api import get_organization
    try:
        return dict(membership=get_organization(request).short_name)
    except:
        return dict(membership="__default__")

selectable_renderer = SelectableRendererSetup(
    RecieveTemplatePathFormat,
    get_template_path_args,
    renderer_name="selectable_renderer"
    )

def includeme(config):
    selectable_renderer.register_to(config)


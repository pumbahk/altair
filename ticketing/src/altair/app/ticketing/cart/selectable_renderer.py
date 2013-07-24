# encoding: utf-8
from pyramid_selectable_renderer import SelectableRendererSetup
from pyramid_selectable_renderer.custom import ReceiveTemplatePathFormat, ReceiveTemplatePathCandidatesDict, SelectByRequestGen

import logging
logger = logging.getLogger(__name__)

@SelectByRequestGen.generate
def get_template_path_args(request):
    from altair.app.ticketing.core.api import get_organization
    try:
        return dict(membership=get_organization(request).short_name)
    except Exception, e:
        logger.warn('membership not found (%s)' % e.message)
        return dict(membership="__default__")

selectable_renderer = SelectableRendererSetup(
    ReceiveTemplatePathFormat,
    get_template_path_args,
    renderer_name="selectable_renderer"
    )

def includeme(config):
    selectable_renderer.register_to(config)


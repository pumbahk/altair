def make_pyramid_mako_renderer_factory_factory():
    from pyramid_mako import MakoRendererFactory, PkgResourceTemplateLookup
    factory = MakoRendererFactory()
    factory.lookup = PkgResourceTemplateLookup()
    return factory

pyramid_mako_compatible_renderer_factory_factory = make_pyramid_mako_renderer_factory_factory()

def pyramid_mako_compatible_renderer_factory(info):
    return pyramid_mako_compatible_renderer_factory_factory(info)

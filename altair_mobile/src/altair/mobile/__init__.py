from pyramid.view import view_config

def includeme(config):
    from .impl import DefaultCarrierDetector
    from .interfaces import IMobileCarrierDetector
    config.add_tween(".tweens.mobile_encoding_convert_factory")
    config.registry.registerUtility(DefaultCarrierDetector(), IMobileCarrierDetector)

def mobile_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.IMobileRequest', 
                       **kwargs)    

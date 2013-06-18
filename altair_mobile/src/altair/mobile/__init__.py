from pyramid.view import view_config

def includeme(config):
    config.include(install_detector)
    config.add_tween(".tweens.mobile_encoding_convert_factory")

def install_detector(config):
    from .impl import DefaultCarrierDetector
    from .interfaces import IMobileCarrierDetector
    config.registry.registerUtility(DefaultCarrierDetector(), IMobileCarrierDetector)


def mobile_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.IMobileRequest', 
                       **kwargs)    

PC_ACCESS_COOKIE_NAME = "_pcaccess"

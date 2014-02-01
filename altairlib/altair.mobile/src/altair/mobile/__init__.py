from pyramid.view import view_config
from altair.extracodecs import register_codecs

def includeme(config):
    config.include(install_detector)
    config.include(install_mobile_request_maker)
    config.add_tween(".tweens.mobile_encoding_convert_factory")
    register_codecs()

def install_detector(config):
    from .impl import DefaultCarrierDetector
    from .interfaces import IMobileCarrierDetector
    config.registry.registerUtility(DefaultCarrierDetector(), IMobileCarrierDetector)

def install_mobile_request_maker(config):
    from pyramid.interfaces import ISession
    from beaker.session import SessionObject
    from .impl import MobileRequestMaker, make_session_object_impl_companion 
    from .interfaces import IMobileRequestMaker, ISessionObjectImplCompanion
    config.registry.registerAdapter(
        make_session_object_impl_companion,
        (ISession,),
        ISessionObjectImplCompanion
        )
    config.registry.registerUtility(
        MobileRequestMaker(
            config.registry.settings.get('altair.mobile.embedded_session_restorer', None)
            ),
        IMobileRequestMaker
        )

def mobile_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.IMobileRequest', 
                       **kwargs)    

def smartphone_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.ISmartphoneRequest',
                       **kwargs)

PC_ACCESS_COOKIE_NAME = "_pcaccess"

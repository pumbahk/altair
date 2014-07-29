import logging
from pyramid.view import view_config
from pyramid.settings import asbool
from altair.extracodecs import register_codecs

logger = logging.getLogger(__name__)

def includeme(config):
    config.include(install_detector)
    config.include(install_mobile_middleware)
    config.include(install_smartphone_support_predicate)
    config.add_tween("%s.tweens.mobile_encoding_convert_factory" % __name__)
    register_codecs()

def install_detector(config):
    from .detector import DefaultCarrierDetector
    from .interfaces import IMobileCarrierDetector
    config.registry.registerUtility(DefaultCarrierDetector(), IMobileCarrierDetector)

def on_error_return_error_response(e, request):
    if isinstance(e, UnicodeDecodeError):
        logger.exception('error during decoding request')
        return Response(status=400, body=str(e))
    else:
        logger.exception('error during encoding response?')
        return Response(status=500, body=str(e))

def install_mobile_middleware(config):
    from .middleware import MobileMiddleware
    from .interfaces import IMobileMiddleware
    encoding = config.registry.settings.get("altair.mobile.encoding", None)
    if encoding is None:
        encoding = 'Shift_JIS'
        logger.warn("settings: altair.mobile.encoding is None. assuming %s" % encoding)
    codec = config.registry.settings.get("altair.mobile.codec", encoding)
    errors = config.registry.settings.get("altair.mobile.errors", "strict")
    on_error_handler = config.registry.settings.get("altair.mobile.on_error_handler", on_error_return_error_response)
    if on_error_handler is not None:
        on_error_handler = config.maybe_dotted(on_error_handler)

    config.registry.registerUtility(
        MobileMiddleware(
            encoding=encoding,
            codec=codec,
            errors=errors,
            on_error_handler=on_error_handler
            ),
        IMobileMiddleware
        )

def install_smartphone_support_predicate(config):
    from .predicates import DefaultSmartphoneSupportPredicate
    from .interfaces import ISmartphoneSupportPredicate
    smartphone_support_enabled = config.registry.settings.get("altair.mobile.enable.smartphone")
    if smartphone_support_enabled is None:
        logger.warn("settings: altair.mobile.enable.smartphone not found. disabled.")
    smartphone_support_enabled = asbool(smartphone_support_enabled)
    config.registry.registerUtility(
        DefaultSmartphoneSupportPredicate(smartphone_support_enabled),
        ISmartphoneSupportPredicate
        )

def mobile_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.IMobileRequest', 
                       **kwargs)    

def smartphone_view_config(**kwargs):
    return view_config(request_type=__name__ + '.interfaces.ISmartphoneRequest',
                       **kwargs)

PC_ACCESS_COOKIE_NAME = "_pcaccess"

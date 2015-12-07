from zope.interface import Interface, Attribute

class IMobileCarrier(Interface):
    """Carrier"""
    id = Attribute('''Human-readable identifier that uniquely identifiers the carrier''')
    name = Attribute('''Name of the carrier''')
    is_docomo = Attribute('''True if the carrier is DoCoMo''')
    is_ezweb = Attribute('''True if the carrier is EZweb''')
    is_softbank = Attribute('''True if the carrier is SoftBank''')
    is_willcom = Attribute('''True if the carrier is Willcom''')
    is_nomobile = Attribute('''True if non-mobile''')

class IMobileUserAgentDisplayInfo(Interface):
    width = Attribute('''width''')
    height = Attribute('''height''')
    depth = Attribute('''depth''')
    color = Attribute('''color''')
    width_bytes = Attribute('''width_bytes''')
    height_bytes = Attribute('''height_bytes''')

class IMobileUserAgent(Interface):
    """Carrier"""
    carrier = Attribute('''The carrier object''')
    normalized_string = Attribute('''Normalized user-agent string''')
    string = Attribute('''User-agent string''')
    unique_opaque = Attribute('''An identifier that is virtually unique amongst the subscribers.  DO NOT RELY ON IT''')
    supports_cookie = Attribute('''True if the client supports Cookie''')

    def get_display_info():
        '''Returns the display information of the client'''

class IMobileCarrierDetector(Interface):
    """IMobileCarrierDetector"""
    def detect_from_email_address(address):
        """Returns the carrier object"""

    def detect_from_wsgi_environment(environ):
        """Returns the user agent object"""

    def detect_from_ip_address(address):
        """Returns the carrier object"""

class IMobileRequest(Interface):
    """ mobile request interface"""
    mobile_ua = Attribute('''Mobile user agent object''')
    io_codec = Attribute('''Codec name used for I/O''')

    def open_form_tag_for_get(**attrs):
        pass

class ISmartphoneRequest(Interface):
    """ smartphone request interface"""
    pass

class IMobileMiddleware(Interface):
    def __call__(handler, request):
        pass

class ISmartphoneSupportPredicate(Interface):
    def __call__(request):
        pass

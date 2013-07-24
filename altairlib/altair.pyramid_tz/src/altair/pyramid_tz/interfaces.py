from zope.interface import Interface, Attribute

class ITimeZone(Interface):
    zone = Attribute('''Textual name of the time zone''')

    def dst(datetime):
        pass

    def fromutc(datetime):
        pass

    def tzname(datetime):
        pass

    def utcoffset(datetime):
        pass

    def localize(datetime, is_dst=False):
        pass

    def normalize(datetime, is_dst=False):
        pass

class ITimeZoneInfoProvider(Interface):
    def __call__(timezone_name):
        pass

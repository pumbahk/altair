from zope.interface import Interface

class IDatetimeFormatter(Interface):
    def format_datetime(date, **flavor):
        pass

    def format_date(date, **flavor):
        pass

    def format_time(time, **flavor):
        pass

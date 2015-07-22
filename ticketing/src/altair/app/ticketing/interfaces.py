from zope.interface import Interface, alsoProvides 

class IAPIContext(Interface):
    pass

class ITicketingFormatter(Interface):
    def sex_as_string(sex):
        pass

    def format_date(date):
        pass

    def format_date_short(date):
        pass

    def format_date_compressed(date):
        pass

    def format_time(time):
        pass

    def format_time_short(time):
        pass

    def format_datetime(datetime):
        pass

    def format_datetime_short(datetime):
        pass

    def format_currency(dec):
        pass


class ITemporaryStore(Interface):
    def set(request, value):
        pass

    def get(request):
        pass

    def clear(request):
        pass

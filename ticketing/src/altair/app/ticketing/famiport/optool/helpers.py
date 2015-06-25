class Helpers(object):
    def __init__(self, request):
        self.request = request

    def test_helper(self):
        return u'test'

class ViewHelpers(object):
    def get_date(self, datetime):
        return "{0:%Y-%m-%d}".format(datetime)

    def get_time(self, datetime):
        return "{0:%H:%M}".format(datetime)

class MailTestMixin(object):
    def registerDummyMailer(self):
        from pyramid_mailer import get_mailer
        from pyramid_mailer.interfaces import IMailer
        self.config.registry.unregisterUtility(get_mailer(self.config.registry), IMailer)
        self.config.include('pyramid_mailer.testing') 

    def assertBodyContains(self, needle, haystack, message=None):
        from pyramid_mailer.message import Attachment
        from cgi import parse_header
        if isinstance(haystack, Attachment):
            ct, ctparams = parse_header(haystack.content_type)
            haystack = haystack.data.decode(ctparams.get('charset', 'UTF-8'))
        self.assertIn(needle, haystack, message)

    def assertBodyDoesNotContain(self, needle, haystack, message=None):
        from pyramid_mailer.message import Attachment
        from cgi import parse_header
        if isinstance(haystack, Attachment):
            ct, ctparams = parse_header(haystack.content_type)
            haystack = haystack.data.decode(ctparams.get('charset', 'UTF-8'))
        self.assertNotIn(needle, haystack, message)



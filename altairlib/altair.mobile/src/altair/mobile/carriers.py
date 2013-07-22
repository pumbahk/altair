from zope.interface import implementer
from .interfaces import IMobileCarrier

@implementer(IMobileCarrier)
class Carrier(object):
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def is_docomo(self):
        return self._is_docomo

    @property
    def is_ezweb(self):
        return self._is_ezweb

    @property
    def is_softbank(self):
        return self._is_softbank

    @property
    def is_willcom(self):
        return self._is_willcom

    @property
    def is_nonmobile(self):
        return self._is_nonmobile

    @property
    def email_address_fqdns(self):
        return self._email_address_fqdns

    def __init__(self, id, name, is_docomo, is_ezweb, is_softbank, is_willcom, is_nonmobile, email_address_fqdns):
        self._id = id
        self._name = name
        self._is_docomo = is_docomo
        self._is_ezweb = is_ezweb
        self._is_softbank = is_softbank
        self._is_willcom = is_willcom
        self._is_nonmobile = is_nonmobile
        self._email_address_fqdns = tuple(email_address_fqdns)

DoCoMo    = Carrier('docomo',    'DoCoMo',     True,  False, False, False, False, ('docomo.ne.jp', ))
EZweb     = Carrier('ezweb',     'EZweb',      False, True,  False, False, False, ('ezweb.ne.jp', 'ido.ne.jp'))
SoftBank  = Carrier('softbank',  'SoftBank',   False, False, True,  False, False, ('softbank.ne.jp', 'vodafone.ne.jp', 'jp-d.ne.jp', 'jp-h.ne.jp', 'jp-t.ne.jp', 'jp-c.ne.jp', 'jp-r.ne.jp', 'jp-k.ne.jp', 'jp-n.ne.jp', 'jp-s.ne.jp', 'jp-q.ne.jp'))
Willcom   = Carrier('willcom',   'WILLCOM',    False, False, False, True,  False, ('willcom.com', 'pdx.ne.jp'))
Crawler   = Carrier('crawler',   'Crawlers',   False, False, False, False, True, ())
NonMobile = Carrier('nonmobile', 'Non-mobile', False, False, False, False, True, () )

carriers = [
    DoCoMo,
    SoftBank,
    Willcom,
    Crawler,
    NonMobile,
    ]

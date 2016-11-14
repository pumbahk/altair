import re
import radix
import logging
from zope.interface import implementer, directlyProvides
from uamobile import detect
from uamobile.context import Context
from uamobile.docomo import DoCoMoUserAgent
from uamobile.ezweb import EZwebUserAgent
from uamobile.softbank import SoftBankUserAgent
from uamobile.willcom import WillcomUserAgent
from uamobile.nonmobile import NonMobileUserAgent
from .carriers import (
    carriers,
    DoCoMo,
    EZweb,
    SoftBank,
    Willcom,
    NonMobile,
    )

from .interfaces import (
    IMobileUserAgent,
    IMobileUserAgentDisplayInfo,
    IMobileCarrierDetector,
    )

## for smartphone
SMARTPHONE_USER_AGENT_RX = re.compile("iPhone|iPod|Opera Mini|Android.*Mobile|NetFront|PSP|BlackBerry")

logging.getLogger(__name__)


@implementer(IMobileUserAgent)
class UAMobileUserAgentWrapper(object):
    impl_map = {
        DoCoMoUserAgent.__name__: DoCoMo,
        EZwebUserAgent.__name__: EZweb,
        SoftBankUserAgent.__name__: SoftBank,
        WillcomUserAgent.__name__: Willcom,
        NonMobileUserAgent.__name__: NonMobile
        }

    uo_fetcher_map = {
        DoCoMoUserAgent.__name__: lambda impl: impl.serialnumber,
        EZwebUserAgent.__name__: lambda impl: impl.serialnumber,
        SoftBankUserAgent.__name__: lambda impl: impl.jphone_uid,
        WillcomUserAgent.__name__: lambda impl: None,
        NonMobileUserAgent.__name__: lambda impl: None,
        }

    @property
    def carrier(self):
       return self._carrier

    @property
    def normalized_string(self):
        return self.impl.strip_serialnumber()

    @property
    def string(self):
        return self.impl.useragent

    @property
    def unique_opaque(self):
        return self._uo_fetcher(self.impl)

    @property
    def supports_cookie(Self):
        return self.impl.supports_cookie()

    def get_display_info(self):
        display_info = self.impl.make_display()
        directlyProvides(display_info, IMobileUserAgentDisplayInfo)
        return display_info

    @property
    def is_smartphone(self):
        return SMARTPHONE_USER_AGENT_RX.search(self.impl.useragent)

    def __init__(self, impl):
        self.impl = impl
        self._carrier = self.impl_map[impl.__class__.__name__]
        self._uo_fetcher = self.uo_fetcher_map[impl.__class__.__name__]


@implementer(IMobileCarrierDetector)
class DefaultCarrierDetector(object):
    def detect_from_fqdn(self, fqdn):
        return self.fqdn_map.get(fqdn, NonMobile)

    def detect_from_wsgi_environment(self, environ):
        return UAMobileUserAgentWrapper(detect(environ, self.uamobile_context)) # XXX

    def detect_from_ip_address(self, address):
        try:
            node = self.cidr_block_trie.search_best(address)
        except ValueError:
            logging.info("The address can't be judged.It's made all except for mobile.IP={}".format(address))
            return NonMobile
        if node is None:
            return NonMobile
        return node.data['carrier']

    def __init__(self, uamobile_context=None):
        self.uamobile_context = uamobile_context or Context()
        self.cidr_block_trie = radix.Radix()
        self.fqdn_map = {}
        # XXX: assuming UAMobile context to be immutable
        for carrier in carriers:
            for cidr_block in self.uamobile_context.get_ip(carrier.id):
                node = self.cidr_block_trie.add(str(cidr_block))
                node.data['carrier'] = carrier
            for fqdn in carrier.email_address_fqdns:
                self.fqdn_map[fqdn] = carrier



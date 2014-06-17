#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import itertools
import sys
import ConfigParser
import argparse
from collections import namedtuple

from altair.devproxy.implementation import MyProxyRequest

SUBDOMAINS = [
    '89ers',
    'happinets',
    'tokyo-cr',
    'vissel',
    'c',
    'rt',
    'bambitious',
    'bigbulls',
    'lakestars',
    'kings',
    'oxtv',
    'eagles',
    'v-varen',
    'bacoo',
    'blaublitz',
    'grouses',
    'tbc',
    'toukon',
    'duojapan',
    'popcircus',
    'sc',
    'jubilo',
    ]

class URLRewriterPatternBuilder(object):
    def __init__(self, subdomains, real_apphost):
        self.subdomains = subdomains
        self.real_apphost = real_apphost

    def backend_rewrite_patterns(self):
        return [
            (r'http://backend.stg2.rt.ticketstar.jp(/qrreader(?:/.*)?)',
             r'http://{hostname}:8030\1'.format(hostname=self.real_apphost)),
            (r'http://backend.stg2.rt.ticketstar.jp(/.*)?',
             r'http://{hostname}:8021\1'.format(hostname=self.real_apphost)),
            (r'http://cms.stg2.rt.ticketstar.jp(/.*)?',
             r'http://{hostname}:8001\1'.format(hostname=self.real_apphost)),
            ]

    def booster_rewrite_patterns(self):
        return [
            (r'http://89ers.stg2.rt.ticketstar.jp(/booster(?:/.*)?)',
             r'http://{hostname}:9081\1'.format(hostname=self.real_apphost)),
            (r'http://bambitious.stg2.rt.ticketstar.jp(/booster(?:/.*)?)',
             r'http://{hostname}:9082\1'.format(hostname=self.real_apphost)),
            (r'http://bigbulls.stg2.rt.ticketstar.jp(/booster(?:/.*)?)',
             r'http://{hostname}:9083\1'.format(hostname=self.real_apphost)),
        ]

    def extra_rewrite_patterns(self):
        return [
            (r'http://dummy-checkout-server.stg2.rt.ticketstar.jp(/.*)',
             r'http://{hostname}:8071\1'.format(hostname=self.real_apphost)),
            ]

    def _create_front_rewrite_patterns_for_subdomain(self, subdomain):
        return [
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/orderreview(?:/.*)?)'.format(subdomain=subdomain),
             r'http://{hostname}:9061\1'.format(hostname=self.real_apphost)),
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/lots(?:/.*)?)'.format(subdomain=subdomain),
             r'http://{hostname}:9121\1'.format(hostname=self.real_apphost)),
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/cart(?:/.*)?)'.format(subdomain=subdomain),
             r'http://{hostname}:9021\1'.format(hostname=self.real_apphost)),
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/whattime(?:/.*)?)'.format(subdomain=subdomain),
             r'http://{hostname}:9071\1'.format(hostname=self.real_apphost)),
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/maintenance(?:/.*)?)'.format(subdomain=subdomain),
             r'http://{hostname}:8000\1'.format(hostname=self.real_apphost)),
            (r'http://{subdomain}.stg2.rt.ticketstar.jp(/.*)?'.format(subdomain=subdomain),
             r'http://{hostname}:9001\1'.format(hostname=self.real_apphost)),
             ]

    def front_rewrite_patterns(self):
        return itertools.chain.from_iterable(
            self._create_front_rewrite_patterns_for_subdomain(subdomain)
            for subdomain in self.subdomains
            )

    def __call__(self):
        return list(itertools.chain.from_iterable(
            getattr(self, attr)()
            for attr in dir(self) if attr[0] != '_' and attr.endswith('_rewrite_patterns')
            ))


class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest
    config = None #xxx: use get_current_registry?

    def create_prerewrite_patterns(self, real_apphost):
        return [
        (r'http://api.ticket.rakuten.co.jp/rid/rc/http/stg/([^/]+)(/.+)?/(verify.*)',
         r'http://\1.stg2.rt.ticketstar.jp\2/\3'),
        ]

    def __init__(self, *args, **kwargs):
        proxy.Proxy.__init__(self, *args, **kwargs)
        app_settings = self.config.settings["app"]
        real_apphost = app_settings.hostname or "localhost"

        self.prerewrite_patterns = self.create_prerewrite_patterns(real_apphost)
        self.rewrite_patterns = URLRewriterPatternBuilder(app_settings.subdomains, real_apphost)()

## setup

def proxy_factory_from_config(config):
    class ProxyFactory(http.HTTPFactory):
        protocol = MyProxy
        protocol.config = config #xxx:
    return ProxyFactory

NetworkSetting = namedtuple("NetworkSetting", "addr, port")
AppSetting = namedtuple("AppSetting", "hostname subdomains")


def setup_app_setting(config):
    args = config.settings["args"]
    hostname = config.settings.get("hostname", args.hostname)
    subdomains = config.settings.get("subdomains")
    if subdomains is None:
        subdomains = SUBDOMAINS
    else:
        subdomains = [x.strip() for x in subdomains.split("\n")]
    config.settings["app"] = AppSetting(hostname=hostname, subdomains=subdomains)

def setup_network_setting(config):
    addr_or_port, semi, port = config.settings["args"].address.partition(':')
    if not semi:
        addr = None
        port = int(addr_or_port)
    else:
        addr = addr_or_port
        port = int(port)
    if not addr:
        addr = ''
    config.settings["network"] = NetworkSetting(addr=addr, port=port)


def setup_logging(config):
    logging_file_name = config.settings["args"].log
    if logging_file_name:
        return open(logging_file_name, 'a')
    else:
        out = sys.stderr
    log.startLogging(out)



class MiniConfigurator(object):
    def __init__(self, settings):
        self.settings = settings

    def include(self, fn):
        return fn(self)

    def run_app(self):
        network = self.settings["network"]
        appsetting = self.settings["app"]
        sys.stderr.write("Forwarding: {}\n".format(appsetting.hostname))
        sys.stderr.write("SubDomains: {}\n".format(", ".join(appsetting.subdomains)))
        sys.stderr.write("Listening on %s:%d\n" % (network.addr, network.port))

        proxy_factory = proxy_factory_from_config(self)
        reactor.listenTCP(network.port, proxy_factory(), 10, network.addr)
        reactor.run()

#config file
"""
hostname = localhost
subdomains =
  89ers
  happinets
  ticketstar
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='log', type=str,
                        help='access log')
    parser.add_argument("-c", "--configfile", dest="configfile", type=str)
    parser.add_argument('address', type=str,
                        help='the server address to listen on')
    parser.add_argument('--hostname', type=str)
    parser.set_defaults(hostname="localhost")

    args = parser.parse_args()
    settings = {"args": args}

    if args.configfile:
        parser = ConfigParser.SafeConfigParser()
        assert parser.read(args.configfile)
        settings.update(parser.items("devproxy"))
    config = MiniConfigurator(settings)

    config.include(setup_app_setting)

    config.include(setup_logging)
    config.include(setup_network_setting)
    config.run_app()

if __name__ == '__main__':
    main()

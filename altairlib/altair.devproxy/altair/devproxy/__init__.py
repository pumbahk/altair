#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import itertools
import sys
import ConfigParser
import argparse
import re
from collections import namedtuple

from altair.devproxy.implementation import MyProxyRequest

class ApplicationException(Exception):
    pass

class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest
    config = None #xxx: use get_current_registry?

    def __init__(self, *args, **kwargs):
        proxy.Proxy.__init__(self, *args, **kwargs)
        self.redirect_patterns = self.config.redirects
        self.prerewrite_patterns = self.config.prerewrites
        self.rewrite_patterns = self.config.rewrites

## setup

def proxy_factory_from_config(config):
    class ProxyFactory(http.HTTPFactory):
        protocol = MyProxy
        protocol.config = config #xxx:
    return ProxyFactory

NetworkSetting = namedtuple("NetworkSetting", "addr, port")
AppSetting = namedtuple("AppSetting", "hostname subdomains")


def parse_add_port_pair(pair):
    addr_or_port, semi, port = pair.partition(':')
    if not semi:
        addr = None
        port = int(addr_or_port)
    else:
        addr = addr_or_port
        port = int(port)
    if not addr:
        addr = ''
    return addr, port

def setup_logging(config):
    logging_file_name = config.settings.get("access_log")
    if logging_file_name:
        out = open(logging_file_name, 'a')
    else:
        out = sys.stderr
    log.startLogging(out)



class MiniConfigurator(object):
    def __init__(self, settings, redirects, prerewrites, rewrites):
        self.settings = settings
        self.redirects = redirects
        self.prerewrites = prerewrites
        self.rewrites = rewrites

    def include(self, fn):
        return fn(self)

    def run_app(self):
        addr, port = parse_add_port_pair(self.settings['listen'])
        message("Listening on %s:%d\n" % (addr, port))

        proxy_factory = proxy_factory_from_config(self)
        reactor.listenTCP(port, proxy_factory(), 10, addr)
        reactor.run()

#config file
"""
hostname = localhost
subdomains =
  89ers
  happinets
  ticketstar
"""

def message(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.stderr.flush()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config", type=str)
    parser.add_argument("-D", "--define", dest="define", nargs='*', type=str, help='default values')
    parser.add_argument('config_value', type=str, nargs='*', help='configuration value (key=value)')

    args = parser.parse_args()

    try:
        settings_from_cmdline = {}
        if args.config_value:
            for pair in args.config_value:
                k, _, v = pair.partition('=')
                settings_from_cmdline[k] = v

        default_values = {}
        if args.define:
            for pair in args.define:
                k, _, v = pair.partition('=')
                default_values[k] = v

        settings = {
            'listen': '0.0.0.0:58080'
            }
        redirects = []
        prerewrites = []
        rewrites = []
        if args.config:
            parser = ConfigParser.SafeConfigParser(default_values)
            if not parser.read(args.config):
                raise ApplicationException('failed to read %s' % args.config)

            for section in parser.sections():
                g = re.match('redirect(?::(?P<category>.*))?', section)
                if g is not None:
                    for name, pair in parser.items(section):
                        if not name.startswith('_'):
                            pair = [x.strip() for x in pair.strip().split('\n', 1)]
                            redirects.append(('%s:%s' % (g.group(1) or '', name), re.compile(pair[0]), pair[1]))
                    continue
                g = re.match('prerewrite(?::(?P<category>.*))?', section)
                if g is not None:
                    for name, pair in parser.items(section):
                        if not name.startswith('_'):
                            pair = [x.strip() for x in pair.strip().split('\n', 1)]
                            prerewrites.append(('%s:%s' % (g.group(1) or '', name), re.compile(pair[0]), pair[1]))
                    continue
                g = re.match('rewrite(?::(?P<category>.*))?', section)
                if g is not None:
                    for name, pair in parser.items(section):
                        if not name.startswith('_'):
                            pair = [x.strip() for x in pair.strip().split('\n', 1)]
                            rewrites.append(('%s:%s' % (g.group(1) or '', name), re.compile(pair[0]), pair[1]))
                    continue
            settings.update(parser.items('devproxy'))

        settings.update(settings_from_cmdline)
        config = MiniConfigurator(settings, redirects, prerewrites, rewrites)

        config.include(setup_logging)
        config.run_app()
    except ApplicationException as e:
        message(e.message)

if __name__ == '__main__':
    main()

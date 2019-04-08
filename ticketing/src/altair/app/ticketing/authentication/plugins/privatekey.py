# encoding: utf-8

from altair.app.ticketing.authentication.plugins import TicketingKeyBaseAuthPlugin

PRIVATEKEY_AUTH_IDENTIFIER_NAME = 'privatekey'


class PrivateKeyAuthPlugin(TicketingKeyBaseAuthPlugin):
    name = PRIVATEKEY_AUTH_IDENTIFIER_NAME

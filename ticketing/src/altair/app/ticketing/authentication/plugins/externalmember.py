# encoding: utf-8

from altair.app.ticketing.authentication.plugins import TicketingKeyBaseAuthPlugin

EXTERNALMEMBER_AUTH_IDENTIFIER_NAME = 'externalmember'
EXTERNALMEMBER_ID_POLICY_NAME = 'externalmember_id'
EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME = 'externalmember_email_address'


class ExternalMemberAuthPlugin(TicketingKeyBaseAuthPlugin):
    name = EXTERNALMEMBER_AUTH_IDENTIFIER_NAME

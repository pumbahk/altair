#! /usr/bin/env python
#-*- coding: utf-8 -*-
import csv
import sys
import time
import argparse
import altair.sqlahelper
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.sej.userside_impl import (
    SejTenantLookup,
    )
import pyramid.request
import pyramid.paster
import pyramid.testing
import transaction

TEST_GATEWAY = 'https://inticket.nrir1test.jp/'

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    opts = parser.parse_args(argv)

    pyramid.paster.setup_logging(opts.conf)
    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings
    request = pyramid.testing.DummyRequest()
    session = altair.sqlahelper.get_db_session(request, 'slave')

    lookup = SejTenantLookup()
    for organization in Organization.query.all():
        status = 'NG'
        try:
            tenant = lookup(request, organization.id)
            if tenant.inticket_api_url == TEST_GATEWAY:
                status = 'OK'
            print status, organization.id, organization.code, tenant.inticket_api_url
        except:
            print status, organization.id, organization.code, 'oh!! no!!'

if __name__ == '__main__':
    main()

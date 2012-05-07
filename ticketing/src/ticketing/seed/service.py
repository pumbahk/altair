# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from datetime import datetime

class ServiceData(DataSet):
    class cms:
        name            = 'Alter CMS'
        key             = 'fa12a58972626f0597c2faee1454e1'
        secret          = 'c5f20843c65870fad8550e3ad1f868'
        redirect_uri    = 'http://127.0.0.1:6543/auth/oauth_callback'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

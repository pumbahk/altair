import os
here = None
def get_here():
     return here
def set_here(v):
    global here
    here = v
    return v

def create_api_key():
    from altaircms.models import DBSession
    from altaircms.auth.models import APIKey
    apikey = APIKey()
    apikey.apikey = apikey.generate_apikey()
    DBSession.add(apikey)
    return apikey

PUSHED_DATA_FROM_BACKEND = None
def get_pushed_data_from_backend():
    global PUSHED_DATA_FROM_BACKEND 
    if PUSHED_DATA_FROM_BACKEND:
        return PUSHED_DATA_FROM_BACKEND[:]
    PUSHED_DATA_FROM_BACKEND = open(os.path.join(get_here(), "functional_tests/event-page-pushed-data-from-backend.json")).read()
    return PUSHED_DATA_FROM_BACKEND[:]

# coding: utf-8
USERS = {
    'editor':'editor',
    'viewer':'viewer'
}
GROUPS = {
    'viewer':['group:viewers'],
    'editor':['group:editors']
}

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])

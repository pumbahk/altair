PREFIX = 'altair.rakuten_auth.claimed_id:'

def get_openid_claimed_id(request):
    for principal in request.effective_principals:
        if principal.startswith(PREFIX):
            return principal[len(PREFIX):]
    return None

def add_claimed_id_to_principals(identities, request):
    if 'rakuten' in identities:
        return ['%s%s' % (PREFIX, identities['rakuten']['claimed_id'])]
    return []


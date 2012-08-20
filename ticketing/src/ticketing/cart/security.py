def auth_model_callback(user, request):
    if not isinstance(user, dict):
        return []
    principals = []
    if 'membership' in user:
        principals.append("membership:%s" % user['membership'])
    if 'membergroup' in user:
        principals.append("membergroup:%s" % user['membergroup'])

    if 'clamed_id' in user:
        principals.append("rakuten_auth")
    return principals

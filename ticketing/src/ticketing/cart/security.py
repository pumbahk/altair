import logging

logger = logging.getLogger(__name__)

def auth_model_callback(user, request):
    if not isinstance(user, dict):
        return []
    principals = []
    if 'membership' in user:
        logger.debug('found membership')
        principals.append("membership:%s" % user['membership'])
    if 'membergroup' in user:
        logger.debug('found membergroup')
        principals.append("membergroup:%s" % user['membergroup'])

    if 'clamed_id' in user:
        logger.debug('found clamed_id')
        principals.append("rakuten_auth")
    return principals

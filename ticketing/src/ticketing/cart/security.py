# -*- coding:utf-8 -*-
"""
TODO: cart下にあるのはおかしいので、どこかに移動
"""

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

    if 'claimed_id' in user:
        logger.debug('found claimed_id')
        principals.append("rakuten_auth")
        principals.append("auth_type:rakuten")
    return principals

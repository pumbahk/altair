# encoding: utf-8

import logging

from altair.app.ticketing.models import DBSession
from . import models as user_models

logger = logging.getLogger(__name__)

def get_or_create_user(authenticated_user):
    if authenticated_user is None or authenticated_user.get('is_guest', False):
        return None

    if 'claimed_id' in authenticated_user:
        auth_identifier = authenticated_user['claimed_id']
        membership = 'rakuten'
    elif 'username' in authenticated_user:
        auth_identifier = authenticated_user['username']
        membership = authenticated_user['membership']

    # TODO: 楽天OpenID以外にも対応できるフレームワークを...
    credential = user_models.UserCredential.query.filter(
        user_models.UserCredential.auth_identifier==auth_identifier
    ).filter(
        user_models.UserCredential.membership_id==user_models.Membership.id
    ).filter(
        user_models.Membership.name==membership
    ).first()
    if credential:
        return credential.user
    
    user = user_models.User()
    membership = user_models.Membership.query.filter(user_models.Membership.name=='rakuten').first()
    if membership is None:
        membership = user_models.Membership(name='rakuten')
        DBSession.add(membership)
    credential = user_models.UserCredential(user=user, auth_identifier=auth_identifier, membership=membership)
    DBSession.add(user)
    return user

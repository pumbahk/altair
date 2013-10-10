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
    else:
        raise ValueError('clamed_id, username not in %s' % authenticated_user)

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

def get_or_create_user_from_point_no(point):
    if not point:
        return None

    credential = user_models.UserCredential.query.filter(
        user_models.UserCredential.auth_identifier==point
    ).filter(
        user_models.UserCredential.membership_id==user_models.Membership.id
    ).filter(
        user_models.Membership.name=='rakuten'
    ).first()
    if credential:
        return credential.user

    user = user_models.User()
    membership = user_models.Membership.query.filter(user_models.Membership.name=='rakuten').first()
    if membership is None:
        membership = user_models.Membership(name='rakuten')
        DBSession.add(membership)
    credential = user_models.UserCredential(user=user, auth_identifier=point, membership=membership)
    DBSession.add(user)

    credential = user_models.UserCredential.query.filter(
        user_models.UserCredential.auth_identifier==point
    ).first()
    return credential.user

def create_user_point_account_from_point_no(user_id, point):
    account_number = ""
    if point != "":
        format = "%s-%s-%s-%s"
        account_number = format % (point[:4], point[4:8], point[8:12], point[12:16])

    acc = user_models.UserPointAccount.query.filter(
        user_models.UserPointAccount.user_id==user_id
    ).first()

    if not acc:
        acc = user_models.UserPointAccount()

    acc.user_id = user_id
    acc.account_number = account_number
    acc.type = user_models.UserPointAccountTypeEnum.Rakuten.v
    acc.status = user_models.UserPointAccountStatusEnum.Valid.v
    DBSession.add(acc)
    return acc

def get_user_point_account(user_id):
    acc = user_models.UserPointAccount.query.filter(
        user_models.UserPointAccount.user_id==user_id
    ).first()
    return acc

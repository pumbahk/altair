# encoding: utf-8

import logging
import re
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

def create_user_point_account_from_point_no(user_id, type, account_number):
    assert account_number is not None and account_number != ""

    if int(type) == int(user_models.UserPointAccountTypeEnum.Rakuten.v) and \
       not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', account_number):
        raise ValueError('invalid account number format; %s' % account_number)

    acc = user_models.UserPointAccount.query.filter(
        user_models.UserPointAccount.user_id==user_id
    ).first()

    if not acc:
        acc = user_models.UserPointAccount()

    acc.user_id = user_id
    acc.account_number = account_number
    acc.type = int(type)
    acc.status = user_models.UserPointAccountStatusEnum.Valid.v
    DBSession.add(acc)
    return acc

def get_user_point_account(user_id):
    acc = user_models.UserPointAccount.query.filter(
        user_models.UserPointAccount.user_id==user_id
    ).first()
    return acc

def get_or_create_user_profile(user, data):

    profile = None
    if user.user_profile:
        profile = user.user_profile

    if not profile:
        profile = user_models.UserProfile()

    profile.first_name=data['first_name'],
    profile.last_name=data['last_name'],
    profile.first_name_kana=data['first_name_kana'],
    profile.last_name_kana=data['last_name_kana'],
    profile.zip=data['zip'],
    profile.prefecture=data['prefecture'],
    profile.city=data['city'],
    profile.address_1=data['address_1'],
    profile.address_2=data['address_2'],
    profile.email_1=data['email_1'],
    profile.tel_1=data['tel_1'],

    user.user_profile = profile
    DBSession.add(user)
    return user.user_profile

# -*- coding:utf-8 -*-

import csv
import sqlalchemy.orm as orm
from ticketing.users.models import MemberGroup, UserCredential, Member, User
from ticketing.models import DBSession
import logging
logger = logging.getLogger(__name__)

def edit_membergroup(members, member_group_id):
    members.update({"membergroup_id": member_group_id}, synchronize_session="fetch")

def cached_method(store_field_name):
    def _wrapper(method):
        def _cached(self, key, *args, **kwargs):
            cache = None
            try:
                cache = getattr(self, store_field_name)
            except AttributeError:
                cache = {}
                setattr(self, store_field_name, cache)
    
            if key in cache:
                return cache[key]

            val = method(self, key, *args, **kwargs)
            cache[key] = val
            return val
        return _cached
    return _wrapper

class UserForLoginCartBuilder(object):
    def __init__(self, request):
        self.request = request
        self.membership_id = request.matchdict["membership_id"]
        self.users  = []

    def _find_user_from_db_same_data(self, membergroup_name, loginname, password):
        return User.query\
            .filter(Member.user_id==User.id)\
            .filter(UserCredential.user_id==User.id)\
            .filter(UserCredential.auth_identifier==loginname, UserCredential.membership_id==self.membership_id)\
            .first()


    def build_user_for_login_cart_add_session(self, membergroup_name, loginname, password):
        user = self.build_user_for_login_cart(membergroup_name, loginname, password)
        DBSession.add(user)
        return user

    def build_user_for_login_cart(self, membergroup_name, loginname, password):
        user = self._find_user_from_db_same_data(membergroup_name, loginname, password) or self.build_user()
        membergroup = self.build_membergroup(membergroup_name)

        credential = self.build_credential(loginname, password, membership_id=self.membership_id)
        member = self.build_member(membergroup)

        member.user = user
        credential.user = user
        self.users.append(user)
        return user

    def build_user(self):
        return User()

    @cached_method("_member_groups")
    def build_membergroup(self, membergroup_name):
        return MemberGroup.get_or_create_by_name(membergroup_name, self.membership_id)

    def build_member(self, membergroup):
        return Member.get_or_create_by_member_group(membergroup)

    def build_credential(self, name, password, user_id=None, membership_id=None):
        get_or_create = UserCredential.get_or_create_overwrite_password
        return get_or_create(auth_identifier=name,
                             auth_secret=password,
                             user_id=user_id,
                             membership_id=membership_id)
    
def members_import_from_csv(request, io):
    """ <Membergroup>, <Id>, <Password>を期待
    """
    reader = csv.reader(io, quotechar="''")
    builder = UserForLoginCartBuilder(request)
    for membergroup_name, loginname, password in reader:
        builder.build_user_for_login_cart_add_session(
            membergroup_name, 
            loginname,
            password)
    return builder.users

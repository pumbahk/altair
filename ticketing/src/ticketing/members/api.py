# -*- coding:utf-8 -*-

import csv
from ticketing.users.models import MemberGroup, UserCredential, Member, User
from ticketing.models import DBSession

def edit_membergroup(members, member_group_id):
    members.update({"membergroup_id": member_group_id}, synchronize_session="fetch")

class UserForLoginCartBuilder(object):
    def __init__(self, request):
        self.request = request
        self.member_group_finder = MemberGroupFinder(request)
        self.users  = []

    def build_membergroup(self, membergroup_name):
        return self.member_group_finder(membergroup_name)
    
    def build_user_for_login_cart_with_save(self, membergroup_name, loginname, password):
        user = self.build_user_for_login_cart(membergroup_name, loginname, password)
        DBSession.add(user)
        return user

    def build_user_for_login_cart(self, membergroup_name, loginname, password):
        membergroup = self.member_group_finder(membergroup_name)
        membership_id = membergroup.membership_id
        
        credential = self.build_credential(loginname, password, membership_id=membership_id)
    
        member = self.build_member(membergroup)
        
        user = self._build_userself()
        member.user = user
        credential.user = user
        self.users.append(user)
        return user

    def build_user(self):
        return User()
        
    def build_member(self, membergroup, user_id=None):
        return Member(user_id=user_id, membergroup=membergroup)

    def build_credential(self, name, password, user_id=None, membership_id=None):
        return UserCredential(auth_identifier=name,
                   auth_secret=password,
                   user_id=user_id,
                   membership_id=membership_id)

class MemberGroupFinder(object):
    def __init__(self, request):
        self.cache = {}
        self.request = request
        self.membership_id = request.matchdict["membership_id"]

    def __call__(self, membergroup_name):
        if membergroup_name in self.cache:
            return self.cache[membergroup_name]

        mg =  MemberGroup.filter(MemberGroup.name==membergroup_name, 
                                 MemberGroup.membership_id==self.membership_id).first()
        if mg is None:
            raise Exception("matched member group is not found") #todo: get_or_create
        
        self.cache[membergroup_name] = mg
        return mg
        
    
def members_import_from_csv(request, member_group_finder, io):
    """ <Membergroup>, <Id>, <Password>を期待
    """
    reader = csv.reader(io, quotechar="''")
    builder = UserForLoginCartBuilder(request)
    for membergroup_name, loginname, password in reader:
        builder.build_user_for_login_cart_with_save(
            membergroup_name, 
            loginname,
            password)
    return builder.users

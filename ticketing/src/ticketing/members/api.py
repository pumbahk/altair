# -*- coding:utf-8 -*-

import csv
from ticketing.users.models import MemberGroup, UserCredential, Member, User
from ticketing.models import DBSession

def edit_membergroup(members, member_group_id):
    members.update({"membergroup_id": member_group_id}, synchronize_session="fetch")

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
    ## 重複した値がきたらどうするの？
    """
    reader = csv.reader(io, quotechar="''")
    users = []
    for row in reader:
        membergroup_name, loginname, password = row
        mg = member_group_finder(membergroup_name)
        user = User.create_for_cart_login(mg, loginname, password)
        DBSession.add(user)
        users.append(user)
    return users

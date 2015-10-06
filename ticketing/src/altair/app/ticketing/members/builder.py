
from altair.app.ticketing.users.models import MemberGroup, Member
from altair.app.ticketing.models import DBSession

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
        self.members = []

    def _find_member_from_db_same_data(self, membergroup_name, loginname):
        return Member.query\
            .filter(Member.auth_identifier==loginname, 
                    Member.membership_id==self.membership_id)\
            .first()


    def build_member_for_login_cart_add_session(self, membergroup_name, loginname, password):
        user = self.build_member_for_login_cart(membergroup_name, loginname, password)
        DBSession.add(user)
        return user

    def build_member_for_login_cart(self, membergroup_name, loginname, password):
        member = self._find_member_from_db_same_data(membergroup_name, loginname)
        if member is None: 
            membergroup = self.build_membergroup(membergroup_name)
            member = Member(
                membergroup=membergroup,
                membership=membergroup.membership,
                auth_identifier=loginname,
                auth_secret=password
                )
        else:
            member.password = password
        self.members.append(member)
        return member

    @cached_method("_member_groups")
    def build_membergroup(self, membergroup_name):
        return MemberGroup.get_or_create_by_name(membergroup_name, self.membership_id)

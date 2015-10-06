
from altair.app.ticketing.users.models import MemberGroup, Member, User
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
        self.users  = []

    def _find_user_from_db_same_data(self, membergroup_name, loginname):
        return User.query\
            .join(Member, Member.user_id==User.id)\
            .filter(Member.auth_identifier==loginname, 
                    Member.membership_id==self.membership_id)\
            .first()


    def build_user_for_login_cart_add_session(self, membergroup_name, loginname, password):
        user = self.build_user_for_login_cart(membergroup_name, loginname, password)
        DBSession.add(user)
        return user

    def build_user_for_login_cart(self, membergroup_name, loginname, password):
        user = self._find_user_from_db_same_data(membergroup_name, loginname) or self.build_user()
        membergroup = self.build_membergroup(membergroup_name)
        self.build_member(membergroup=membergroup, user=user, name=loginname, password=password)
        self.users.append(user)
        return user

    def build_user(self):
        return User()

    @cached_method("_member_groups")
    def build_membergroup(self, membergroup_name):
        return MemberGroup.get_or_create_by_name(membergroup_name, self.membership_id)

    def build_member(self, membergroup, user, name, password):
        member = Member.get_or_create_by_user(user, membergroup.membership)
        member.membergroup = membergroup
        member.auth_identifier = name
        member.auth_secret = password
        return member

def add_credential(membership, membergroup, username, password):
    import ticketing.core.models
    from ticketing.users.models import Membership, User, UserCredential, MemberGroup
    
    m = Membership(name=membership)
    mg = MemberGroup(membership=m, name=membergroup)
    u = User(membergroup=mg)
    uc = UserCredential(membership=m,
                        user=u,
                        auth_identifier=username,
                        auth_secret=password)
    
    return u

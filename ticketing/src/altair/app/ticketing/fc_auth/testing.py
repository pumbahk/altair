def add_credential(membership, membergroup, username, password, organization_short_name="testing"):
    import altair.app.ticketing.core.models
    from altair.app.ticketing.core.models import Organization, Host
    from altair.app.ticketing.users.models import Membership, User, UserCredential, MemberGroup, Member
    
    
    org = Organization(short_name=organization_short_name)
    host = Host(host_name="example.com:80", base_url="/login", organization=org)
    ms = Membership(name=membership, organization=org)
    mg = MemberGroup(membership=ms, name=membergroup)
    m = Member(membergroup=mg, membership=ms, auth_identifier=username, auth_secret=password)
    return m

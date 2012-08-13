def add_credential(membership, username, password):
    import ticketing.core.models
    from ticketing.users.models import Membership, User, UserCredential
    
    m = Membership(name=membership)
    u = User()
    uc = UserCredential(membership=m,
                        user=u,
                        auth_identifier=username,
                        auth_secret=password)
    
    return u

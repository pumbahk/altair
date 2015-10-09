from zope.interface import Interface, Attribute


class IRandomStringGenerator(Interface):
    def __call__():
        pass


class IPersistentStore(Interface):
    expiration_time = Attribute('')

    def __getitem__(k):
        pass

    def __setitem__(k, v):
        pass

    def __contains__(k):
        pass

    def __delitem__(k):
        pass


class IClient(Interface):
    client_id = Attribute('')
    authorized_scope = Attribute('')

    def validate_secret(client_secret):
        pass

    def validate_redirect_uri(redirect_uri):
        pass


class IClientRepository(Interface):
    def lookup(client_id):
        pass


class IScopeManager(Interface):
    def exists(scope):
        pass


class INowGetter(Interface):
    def __call__():
        pass


class IOAuthProviderFactory(Interface):
    def __call__(client_repository, scope_manager, now_getter, code_store, code_generator, access_token_store, access_token_generator, refresh_token_store, refresh_token_generator):
        pass


class IOAuthProvider(Interface):
    def validate_scope(scope):
        pass

    def validated_client(client_id, client_secret):
        pass

    def grant_authorization_code(client_id, redirect_uri=None, scope=None, identity=None):
        pass

    def issue_access_token(code, client_id, client_secret=None, token_type=u'bearer', redirect_uri=None):
        pass

    def revoke_access_token(client_id, client_secret, access_token):
        pass

    def get_identity_by_code(code):
        pass

    def get_auth_descriptor_by_token(access_token):
        pass


class IOpenIDProvider(Interface):
    pass

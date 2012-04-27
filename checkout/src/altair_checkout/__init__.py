from .interfaces import ISigner

def includeme(config):
    """ 
    あんしん決済 サービスID
    あんしん決済 アクセスキー 
    あんしん決済 Success URL
    あんしん決済 Fail URL 
    """

    utilities = config.registry.utilities

    utilities.register(config.maybe_dotted('.api.sign_hmac_sha1'), ISigner, name="hmac-sha1")
    utilities.register(config.maybe_dotted('.api.sign_hmac_md5'), ISigner, name="hmac-md5")

    
    

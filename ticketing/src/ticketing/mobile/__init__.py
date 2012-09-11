from pyramid.view import view_config

def includeme(config):
    config.add_tween(".tweens.mobile_encoding_convert_factory")


def mobile_view_config(**kwargs):
    return view_config(request_type='ticketing.cart.interfaces.IMobileRequest', 
                       **kwargs)    

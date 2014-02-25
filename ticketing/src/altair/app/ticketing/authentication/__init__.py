from .policies import *

def includeme(config):
    from .config import add_challenge_view
    config.add_directive('add_challenge_view', add_challenge_view, action_wrap=True)



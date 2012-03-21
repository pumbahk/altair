
def setup(env):
    from altaircms.models import DBSession
    env["S"] =  DBSession
    from altaircms.models import Base
    env["Base"] =  Base
    env["M"] = Base.metadata

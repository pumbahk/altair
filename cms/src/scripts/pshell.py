
def setup(env):
    from altaircms.models import DBSession
    env["S"] =  DBSession
    from altaircms.models import Base
    env["Base"] =  Base
    env["M"] = Base.metadata
    from altaircms.page.models import Page
    env["Page"] = Page
    from altaircms.widget.models import Widget
    env["Widget"] = Widget


from sqlalchemy import engine_from_config, pool
import sqlahelper
import argparse
import os.path
from alembic.config import Config
from alembic.util import load_python_file

## copy from ../env.py this is not good
import altaircms.models as models
import altaircms.auth.models
import altaircms.asset.models
import altaircms.widget.models
import altaircms.page.models
import altaircms.usersetting.models
import altaircms.event.models
import altaircms.topic.models
import altaircms.layout.models
import altaircms.tag.models
import altaircms.plugins.widget.countdown.models
import altaircms.plugins.widget.image.models
import altaircms.plugins.widget.menu.models
import altaircms.plugins.widget.detail.models
import altaircms.plugins.widget.performancelist.models
import altaircms.plugins.widget.anchorlist.models
import altaircms.plugins.widget.reuse.models
import altaircms.plugins.widget.calendar.models
import altaircms.plugins.widget.heading.models
import altaircms.plugins.widget.flash.models
import altaircms.plugins.widget.breadcrumbs.models
import altaircms.plugins.widget.summary.models
import altaircms.plugins.widget.movie.models
import altaircms.plugins.widget.freetext.models
import altaircms.plugins.widget.promotion.models
import altaircms.plugins.widget.ticketlist.models
import altaircms.plugins.widget.topic.models
import altaircms.plugins.widget.purchase.models
import altaircms.plugins.widget.linklist.models
import altaircms.plugins.widget.iconset.models
import altaircms.plugins.widget.twitter.models


target_metadata = models.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.



def main():
    """
    args.config
    args.files
    args.action default is upgrade
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help=u"config file (e.g. development.ini or alembic.ini)", 
                        nargs="?", default="development.ini")
    parser.add_argument("--action", default="upgrade", help="upgrade, downgrade(default upgrade)")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    return _main(args)

def _main(args):
    config = Config(args.config)
    engine = engine_from_config(config.get_section("alembic"), poolclass=pool.NullPool)
    sqlahelper.add_engine(engine)
    action = args.action #upgrade/downgrade

    try:
        for f in args.files:
            d = os.path.dirname(f)
            f = os.path.basename(f)
            m = load_python_file(d, f)
            if hasattr(m, action):
                getattr(m, action)()
    except Exception:
        import transaction
        transaction.abort() ## this is not failsafe
        raise

main()

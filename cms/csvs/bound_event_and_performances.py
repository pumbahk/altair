import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dburl")
args = parser.parse_args()

import altaircms.models
import altaircms.page.models
import altaircms.event.models

def main(args):
    import sqlalchemy as sa
    import sqlahelper
    engine = sa.create_engine(args.dburl)
    sqlahelper.add_engine(engine)

    from altaircms.event.models import Event
    from altaircms.models import Performance

    session = sqlahelper.get_session()
    qs = session.query(Event, Performance)
    for e, p in qs.filter(Event.title==Performance.title):
        p.event = e
        session.add(p)
    import transaction
    transaction.commit()

if __name__ == "__main__":
    main(args)

import sys
import argparse
import six
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy import orm
from locale import setlocale, nl_langinfo, LC_ALL, CODESET
from datetime import datetime
from dateutil.relativedelta import relativedelta

def main(_args):
    setlocale(LC_ALL, '')
    charset = nl_langinfo(CODESET)
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', required=True)
    parser.add_argument('--last-name', required=True)
    parser.add_argument('--first-name', required=True)
    parser.add_argument('--claimed-id', required=True)
    parser.add_argument('--membership', nargs='*')
    args = parser.parse_args(_args[1:])
    setup_logging(args.config)
    env = bootstrap(args.config)

    from ..models import EaglesUser, EaglesMemberKind, EaglesMembership

    session = env['registry'].sa_session_maker()
    now = datetime.now()

    user = None
    try:
        user = session.query(EaglesUser).filter(EaglesUser.openid_claimed_id == args.claimed_id).one()
    except orm.exc.NoResultFound:
        pass

    if user is None:
        user = EaglesUser(
            last_name=six.text_type(args.last_name, charset),
            first_name=six.text_type(args.first_name, charset),
            openid_claimed_id=six.text_type(args.claimed_id, charset)
            )
        session.add(user)

    if args.membership is not None:
        for kind_name, _, membership_id in (six.text_type(_, charset).partition(u':') for _ in args.membership):
            kind = session.query(EaglesMemberKind).filter_by(name=kind_name).one()
            user.memberships.append(
                EaglesMembership(
                    kind=kind,
                    membership_id=membership_id,
                    valid_since=now,
                    expire_at=now + relativedelta(years=1),
                    )
                )
    session.commit()

if __name__ == '__main__':
    main(sys.argv)

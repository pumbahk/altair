import os
import sys
import transaction
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from pyramid.paster import bootstrap, setup_logging
from argparse import ArgumentParser
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.lots.models import LotEntry, LotEntryWish
from altair.app.ticketing.core.models import MailTypeEnum

def error(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(1)

lots_mail_types = [
    int(MailTypeEnum.LotsAcceptedMail),
    int(MailTypeEnum.LotsElectedMail),
    int(MailTypeEnum.LotsRejectedMail),
    ]

def get_object_by_mail_type(request, session, mail_type, order_or_entry_no):
    if int(mail_type) in lots_mail_types:
        try:
            lot_entry = session.query(LotEntry).filter_by(entry_no=order_or_entry_no).one()
            elected_wish = None
            if mail_type == int(MailTypeEnum.LotsElectedMail):
                elected_wish = session.query(LotEntryWish).filter(LotEntryWish.lot_entry_id == lot_entry.id, LotEntryWish.elected_at != None).one()
            obj = (lot_entry, elected_wish)
        except NoResultFound:
            obj = None
    else:
        obj = get_order_by_order_no(request, order_or_entry_no, session=session)
    return obj

def do_process(request, mail_type, in_, dry_run=False):
    mail_type = int(mail_type)
    session = get_db_session(request, 'slave')
    mutil = get_mail_utility(request, mail_type)
    for order_or_entry_no in in_:
        order_or_entry_no = order_or_entry_no.rstrip()
        sys.stdout.write(order_or_entry_no + "\n")
        sys.stdout.flush()
        try:
            obj = get_object_by_mail_type(request, session, mail_type, order_or_entry_no)
            if obj is None:
                msg = u'not found'
            else:
                if not dry_run:
                    mutil.send_mail(request, obj)
                    transaction.commit()
                msg = u'OK'
        except Exception as e:
            msg = str(e)
            transaction.abort()
        sys.stdout.write("%s\t%s\n" % (order_or_entry_no, msg))
        sys.stdout.flush()
    sys.stdout.write("done\n")
    sys.stdout.flush()

def main():
    parser = ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('--type', metavar='type', type=str, choices=[v.k for v in MailTypeEnum], required=True)
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('files', metavar='file', nargs='*', type=str)
    opts = parser.parse_args()

    setup_logging(opts.config)
    env = bootstrap(opts.config)

    mail_type = getattr(MailTypeEnum, opts.type, None)
    if len(opts.files) == 0:
        in_ = sys.stdin
        do_process(env['request'], mail_type, in_, dry_run=opts.dry_run)
    else:
        for f in opts.files:
            os.stat(f)

        for f in opts.files:
            with open(f) as in_:
                do_process(env['request'], mail_type, in_, opts.dry_run)

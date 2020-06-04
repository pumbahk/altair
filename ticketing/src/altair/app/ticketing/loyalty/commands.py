# encoding: utf-8

import os
import sys
import re
import transaction
import argparse
import logging

from datetime import datetime, timedelta
from dateutil.parser import parse as parsedatetime
from decimal import Decimal

from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.utils import todatetime
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID

logger = logging.getLogger(__name__)

# orgs_with_rakuten: 楽チケと一緒にポイント付与したいOrgのコード, orgs_not_consider_rakutepay: 楽天ペイの場合は対象外にするOrgのコード
from . import orgs_with_rakuten, orgs_not_consider_rakutenpay

class RecordError(Exception):
    pass

class PointGrantHistoryEntryIdDecodeError(RecordError):
    pass

class ColumnNumberMismatchError(RecordError):
    pass

def refund_point_grant_history_entry_id(id, seq_no):
    return u'APHE%ld%02d' % (id, seq_no)

def encode_point_grant_history_entry_id(id):
    return u'APHE%ld' % id

def decode_point_grant_history_entry_id(s):
    g = re.match(ur'APHE(\d+)', s)
    if not g:
        raise PointGrantHistoryEntryIdDecodeError(s)
    try:
        return long(g.group(1))
    except ValueError:
        raise PointGrantHistoryEntryIdDecodeError(s)

def lookup_point_grant_history_entry(type, org_ids=None, order_no=None, account_number=None):
    from .models import PointGrantHistoryEntry
    from altair.app.ticketing.orders.models import Order, order_user_point_account_table
    from altair.app.ticketing.users.models import User

    def add_conditions(q):
        if order_no is not None: 
            q = q.filter(Order.order_no == order_no)
        if org_ids is not None:
            q = q.filter(Order.organization_id.in_(org_ids))
        if type is not None:
            q = q.filter(UserPointAccount.type == type)
        if account_number is not None:
            q = q.filter(UserPointAccount.account_number == account_number)
        return q

    base_q = PointGrantHistoryEntry.query.join(PointGrantHistoryEntry.order)
    try:
        return add_conditions(base_q.join(Order.user_point_accounts)).one()
    except NoResultFound:
        return add_conditions(base_q.join(Order.user).join(User.user_point_accounts)).one()

def build_user_point_account_queries(type, order, account_number=None):
    from altair.app.ticketing.users.models import UserPointAccount
    from altair.app.ticketing.orders.models import Order, order_user_point_account_table

    def add_conditions(q):
        if account_number is not None:
            q = q.filter(UserPointAccount.account_number == account_number)
        if type is not None:
            q = q.filter(UserPointAccount.type == type)
        return q

    queries = [ 
        add_conditions(
            UserPointAccount.query \
                .join(order_user_point_account_table, UserPointAccount.id == order_user_point_account_table.c.user_point_account_id) \
                .join(Order, order_user_point_account_table.c.order_id == Order.id) \
                .filter(Order.id == order.id)
            )
        ]

    if order.user_id is not None:
        queries.append(
            add_conditions(
                UserPointAccount.query \
                    .filter(UserPointAccount.user_id == order.user_id)
                )
            )
    return queries

def lookup_user_point_account(order, type, account_number=None):
    queries = build_user_point_account_queries(type, order, account_number)
    last_exception = None
    for query in queries:
        try:
            return query.one()
        except NoResultFound as e:
            last_exception = e
            continue
    if last_exception is None:
        raise NoResultFound()
    else:
        raise e

def lookup_user_point_accounts(order, type=None, account_number=None):
    queries = build_user_point_account_queries(type, order, account_number)
    for query in queries:
        retval = query.all()
        if len(retval) > 0:
            return retval
    return []

def lookup_for_point_granted_order(order_no, organization):
    from altair.app.ticketing.orders.models import Order

    org_ids = build_org_id_as_list(organization)
    try:
        order = Order.query \
                     .filter(Order.order_no == order_no) \
                     .filter(Order.organization_id.in_(org_ids)) \
                     .one()
        return order
    except NoResultFound:
        raise RecordError("Order(order_no=%s) does not exist" % order_no)


def build_export_data_query(organization, submitted_on, type):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.users.models import UserPointAccount
    from altair.app.ticketing.orders.models import Order
    from .models import PointGrantHistoryEntry

    org_ids = build_org_id_as_list(organization)

    query = DBSession.query(PointGrantHistoryEntry) \
        .filter(PointGrantHistoryEntry.submitted_on == submitted_on) \
        .join(PointGrantHistoryEntry.order) \
        .join(PointGrantHistoryEntry.user_point_account) \
        .filter(UserPointAccount.type == type) \
        .filter(Order.organization_id.in_(org_ids)) \
        .filter(Order.deleted_at == None)

    return query

def build_org_id_as_list(organization, extra_orgs=None):
    from altair.app.ticketing.core.models import Organization, OrganizationSetting
    # orgs_with_rakutenはこのmoduleの__init__.pyにて定義されてる
    with_rakuten = extra_orgs or orgs_with_rakuten
    org_ids = []
    if organization.code == "RT":
        # 一緒に付与するOrgを抽出する
        # point_typeが1（楽天ポイント）ではないやつを対象外にする
        target_orgs = with_rakuten + ["RT"]
        orgs = Organization.query \
            .join(OrganizationSetting) \
            .filter(Organization.code.in_(target_orgs)) \
            .filter(OrganizationSetting.point_type == 1) \
            .all()
        org_ids = [org.id for org in orgs]
    else:
        org_ids = [organization.id]

    return org_ids

def do_import_point_grant_results(registry, organization, file, now, type, force, encoding):
    from .models import PointGrantHistoryEntry
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.users.models import User, UserPointAccount, UserPointAccountTypeEnum

    # 楽天チケットと一緒にポイント付与の場合は何もしない。
    if organization.code in orgs_with_rakuten:
        logger.info(
            "Importing point grant results of this organization(id=%ld, name=%s) is executed within Rakuten Ticket. Skipping" % (
            organization.id, organization.name))

    else:
        logger.info("start importing point granting results for Organization(id=%ld) from %s" % (organization.id, file))
        for line_no, line in enumerate(open(file)):
            try:
                line = line.rstrip('\r\n').decode(encoding)
                cols = line.split('\t')
                if len(cols) < 7 or len(cols) > 9:
                    raise ColumnNumberMismatchError(len(cols))

                if len(cols) == 7:
                    grant_status = u''
                else:
                    grant_status = cols[7]

                account_number = cols[1]
                order_no = cols[3]

                try:
                    points_granted = Decimal(cols[5])
                except ValueError:
                    raise RecordError(u'Invalid point amount', cols[5])

                # 紐づく予約情報を取れないと、RecordErrorのエラーを出す。
                # ここはポイント付与される予約の存在をチェックするのみ。
                order = lookup_for_point_granted_order(order_no=order_no, organization=organization)

                point_grant_history_entry = None
                point_grant_history_entry_id = None

                try:
                    point_grant_history_entry_id = decode_point_grant_history_entry_id(cols[4])
                    try:
                        point_grant_history_entry = PointGrantHistoryEntry.query.filter_by(id=point_grant_history_entry_id).one()
                    except NoResultFound:
                        raise RecordError(u'No corresponding point grant history record found for %ld' % point_grant_history_entry_id)
                except:
                    if not force:
                        raise
                    if not type:
                        raise RecordError(u'If you want to use force option, you have to specify point type via -t')
                    try:
                        org_ids = build_org_id_as_list(organization)
                        point_grant_history_entry = lookup_point_grant_history_entry(
                            organization_id=org_ids,
                            order_no=order_no,
                            type=type,
                            account_number=account_number
                            )
                        point_grant_history_entry_id = point_grant_history_entry.id
                    except:
                        pass

                if point_grant_history_entry is None:
                    raise RecordError(u'Could not determine point grant history record')

                if point_grant_history_entry.user_point_account.type != UserPointAccountTypeEnum.Rakuten.v:
                    raise RecordError(u'UserPointAccount(id=%ld).account_type is not Rakuten' % (point_grant_history_entry.user_point_account.id))

                if point_grant_history_entry.user_point_account.account_number != account_number:
                    raise RecordError(u'UserPointAccount(id=%ld).account_number != %s' % (point_grant_history_entry.user_point_account.id, account_number))
                if point_grant_history_entry.granted_at is not None:
                    raise RecordError(u'PointGrantHistoryEntry(id=%ld) seems to have been processed already' % point_grant_history_entry_id)

                point_grant_history_entry.granted_amount = points_granted
                point_grant_history_entry.grant_status = grant_status
                point_grant_history_entry.granted_at = now

                if not grant_status:
                    logger.info('%d point(s) marked granted for PointGrantHistoryEntry(id=%ld)' % (points_granted, point_grant_history_entry_id))
                else:
                    notify_point_granting_failed(request, point_grant_history_entry)
                    logger.info('Point not granted for PointGrantHistoryEntry(id=%ld) (status: %s)' % (point_grant_history_entry_id, grant_status))
                DBSession.add(point_grant_history_entry)

            except RecordError as e:
                logger.warning("invalid record at line %d skipped (reason: %r)\n" % (line_no + 1, e))
        logger.info("end importing point granting results for Organization(id=%ld) from %s" % (organization.id, file))

def import_point_grant_results():
    import locale
    locale.setlocale(locale.LC_ALL, '')

    if hasattr(locale, 'nl_langinfo'):
        default_encoding = locale.nl_langinfo(locale.CODESET)
    else:
        default_encoding = 'ascii'

    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--organization', required=True)
    parser.add_argument('-e', '--encoding')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-t', '--type')
    parser.add_argument('config')
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    type = None

    if args.type is not None:
        from altair.app.ticketing.users.models import UserPointAccountTypeEnum
        try:
            type = getattr(UserPointAccountTypeEnum, args.type).v
        except:
            sys.stderr.write("Invalid point type: %s\n" % args.type)
            sys.stderr.flush()
            sys.exit(255)

    now = datetime.now()

    transaction.begin()
    try:
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Organization
        organization = None
        try:
            organization = DBSession.query(Organization) \
                .filter(
                    (Organization.name == args.organization) \
                    | (Organization.id == args.organization)
                    ) \
                .one()
        except:
            sys.stderr.write("no such organization: %s\n" % args.organization)
            sys.stderr.flush()
            sys.exit(255)

        for file in args.file:
            do_import_point_grant_results(
                env['registry'],
                organization,
                file,
                now,
                type,
                args.force,
                args.encoding or default_encoding
                )
        transaction.commit()
    except:
        transaction.abort()
        raise

def do_import_point_grant_data(registry, organization, type, submitted_on, file, reason_code, shop_name, encoding, force, deduce_account, recovery):
    from .models import PointGrantHistoryEntry
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.users.models import UserPointAccount, UserPointAccountTypeEnum

    logger.info("start processing %s" % file)

    # 楽天チケットと一緒にポイント付与の場合は何もしない。
    if organization.code in orgs_with_rakuten:
        logger.info(
            "Importing point grant results of this organization(id=%ld, name=%s) is executed within Rakuten Ticket. Skipping" % (
                organization.id, organization.name))

    else:
        errors = 0
        for line_no, line in enumerate(open(file)):
            try:
                line = line.rstrip('\r\n').decode(encoding)
                cols = line.split('\t')
                if len(cols) < 7 or len(cols) > 9:
                    raise ColumnNumberMismatchError(len(cols))

                if len(cols) == 7:
                    status = u''
                else:
                    status = cols[7]

                account_number = cols[1]
                order_no = cols[3]
                try:
                    points_granted = Decimal(cols[5])
                except ValueError:
                    raise RecordError(u'Invalid point amount', cols[5])

                # 紐づく予約情報を取れないと、RecordErrorのエラーを出す。
                # ここはポイント付与される予約の存在をチェックするのみ。
                order = lookup_for_point_granted_order(order_no=order_no, organization=organization)

                if not account_number:
                    if deduce_account:
                        try:
                            user_point_account = lookup_user_point_account(order=order, type=type)
                        except NoResultFound:
                            raise RecordError("UserPointAccount(type=%d, account_number=%s) does not exist" % (type, account_number))
                        except MultipleResultsFound:
                            raise RecordError("multiple UserPointAccount found for the criteria (type=%d, user_id=%d <= order_no=%s) " % (type, order.user_id, order_no))
                    else:
                        raise RecordError("no account number is given for order (order_no=%s). Use --deduce-account option to enable automatic deduction of point account number" % (order_no,))
                else:
                    try:
                        user_point_account = lookup_user_point_account(order=order, type=type, account_number=account_number)
                    except NoResultFound:
                        raise RecordError("UserPointAccount(type=%d, account_number=%s) does not exist" % (type, account_number))
                    except MultipleResultsFound:
                        raise RecordError("multiple UserPointAccount record found (type=%d, account_number=%s)" % (type, account_number))

                if recovery:
                    point_grant_history_entry_id = decode_point_grant_history_entry_id(cols[4])
                    point_grant_history_entry = PointGrantHistoryEntry.query.filter_by(id=point_grant_history_entry_id).first()
                    if point_grant_history_entry is not None:
                        raise RecordError("PointAcountHistoryEntry(id=%ld) already exists for Order(id=%ld, order_No=%s)." % (point_grant_history_entry.id, point_grant_history_entry.order.id, point_grant_history_entry.order.order_no))

                    point_grant_history_entry = PointGrantHistoryEntry(
                        id=point_grant_history_entry_id,
                        user_point_account=user_point_account,
                        order=order,
                        amount=points_granted,
                        submitted_on=submitted_on
                        )
                else:
                    if not force:
                        point_grant_history_entry = PointGrantHistoryEntry.query \
                            .filter(PointGrantHistoryEntry.order_id == order.id) \
                            .filter(PointGrantHistoryEntry.user_point_account_id == user_point_account.id) \
                            .first()

                        if point_grant_history_entry is not None:
                            raise RecordError("PointAcountHistoryEntry(id=%ld) already exists for Order(id=%ld, order_No=%s). Use -f option to forcefully create a new entry" % (point_grant_history_entry.id, order.id, order_no))

                    point_grant_history_entry = PointGrantHistoryEntry(
                        user_point_account=user_point_account,
                        order=order,
                        amount=points_granted,
                        submitted_on=submitted_on
                        )
                DBSession.add(point_grant_history_entry)
                DBSession.flush()

                logger.info(u'PointAcountHistoryEntry(user_point_account=UserPointAccount(id=%ld, type=%d, account_number=%s), order=Order(id=%ld, order_no=%s), amount=%s, submitted_on=%s) created' % (
                    user_point_account.id,
                    user_point_account.type,
                    user_point_account.account_number,
                    order.id,
                    order.order_no,
                    points_granted,
                    submitted_on))

                if reason_code and shop_name:
                    cols = [
                        point_grant_history_entry.order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        point_grant_history_entry.user_point_account.account_number,
                        reason_code,
                        point_grant_history_entry.order.order_no,
                        encode_point_grant_history_entry_id(point_grant_history_entry.id),
                        unicode(point_grant_history_entry.amount.to_integral()),
                        shop_name,
                        ''
                        ]
                    sys.stdout.write(u'\t'.join(cols).encode(encoding))
                    sys.stdout.write("\n")
            except RecordError as e:
                logger.warning("invalid record skipped at line %d (%r)\n" % (line_no + 1, e))
                errors += 1
        logger.info('end processing %s' % file)
        return errors

def import_point_grant_data():
    import locale
    locale.setlocale(locale.LC_ALL, '')

    if hasattr(locale, 'nl_langinfo'):
        default_encoding = locale.nl_langinfo(locale.CODESET)
    else:
        default_encoding = 'ascii'

    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--organization', required=True)
    parser.add_argument('-e', '--encoding')
    parser.add_argument('-t', '--type')
    parser.add_argument('-R', '--reason-code')
    parser.add_argument('-S', '--shop-name')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('--deduce-account', action='store_true')
    parser.add_argument('-Y', '--recovery', action='store_true')
    parser.add_argument('config')
    parser.add_argument('submitted_on')
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    try:
        submitted_on = parsedatetime(args.submitted_on).date()
    except:
        sys.stderr.write("Invalid date: %s\n" % args.submitted_on)
        sys.stderr.flush()
        sys.exit(255)

    from altair.app.ticketing.users.models import UserPointAccountTypeEnum
    try:
        type = getattr(UserPointAccountTypeEnum, args.type or 'Rakuten').v
    except:
        sys.stderr.write("Invalid point type: %s\n" % args.type)
        sys.stderr.flush()
        sys.exit(255)

    reason_code = args.reason_code and args.reason_code.decode(default_encoding)
    shop_name = args.shop_name and args.shop_name.decode(default_encoding)

    setup_logging(args.config)
    env = bootstrap(args.config)

    transaction.begin()

    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Organization
    organization = None
    try:
        organization = DBSession.query(Organization) \
            .filter(
                (Organization.name == args.organization) \
                | (Organization.code == args.organization) \
                | (Organization.short_name == args.organization) \
                | (Organization.id == args.organization)
                ) \
            .one()
    except:
        sys.stderr.write("No such organization: %s\n" % args.organization)
        sys.stderr.flush()
        sys.exit(255)

    try:
        errors = 0
        for file in args.file:
            errors += do_import_point_grant_data(
                env['registry'],
                organization,
                type,
                submitted_on,
                file,
                reason_code,
                shop_name,
                args.encoding or default_encoding,
                args.force,
                args.deduce_account,
                args.recovery
                )
        if errors > 0 and not args.force:
            sys.stderr.write("%d errors detected. aborting...\n" % errors)
            transaction.abort()
            sys.exit()
        else:
            transaction.commit()
    except:
        transaction.abort()
        raise

def do_make_point_grant_data(registry, organization, start_date, end_date, submitted_on):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Performance, Event, Organization, OrganizationSetting
    from altair.app.ticketing.orders.models import Order
    from .models import PointGrantHistoryEntry
    from .api import calculate_point_for_order

    logger.info("start processing for orders whose performance has ended in the period %s to %s" % (start_date, end_date))

    if organization is not None:
        organizations = [organization]
    else:
        organizations = DBSession.query(Organization).all()

    for organization in organizations:
        if not organization.setting.point_type:
            logger.info("Organization(id=%ld, name=%s) doesn't have point granting feature enabled. Skipping" % (organization.id, organization.name))
            continue

        logger.info("start processing orders for Organization(id=%ld)" % organization.id)

        query = DBSession.query(Order)\
                         .join(Order.performance) \
                         .join(Performance.event) \
                         .filter(Event.organization_id == organization.id) \
                         .filter(Order.canceled_at == None) \
                         .filter(Order.refunded_at == None) \
                         .filter(Order.refund_id == None) \
                         .filter(Order.paid_at != None) \
                         .filter(Order.manual_point_grant == False) # Only select auto grant mode
        import ast
        org_info_dict = ast.literal_eval(registry.settings.get('altair.make_point_grant.month_org_info', '{}'))
        logger.info("month_org_info is %s and current code is %s" % (org_info_dict, organization.code))
        if organization.code in org_info_dict and submitted_on.day == org_info_dict.get(organization.code):
            from dateutil.relativedelta import relativedelta
            # レジャーチケットは公演日の概念がないため、前月の購入データというルールです
            # 毎月の25でRL前月のOrdersを取って来るようにする。
            """ Example:
            >>> submitted_on = parsedatetime('20200625').date()
            >>> paid_start_date = todatetime(submitted_on - relativedelta(months=1)).replace(day=1)
            >>> paid_start_date
            datetime.datetime(2020, 5, 1, 0, 0)
            >>> submitted_on.replace(day=1)
            datetime.date(2020, 6, 1)
            """
            paid_start_date = todatetime(submitted_on - relativedelta(months=1)).replace(day=1)
            paid_end_date = submitted_on.replace(day=1)
            query = query.filter(Order.paid_at >= paid_start_date).filter(Order.paid_at < paid_end_date)

            logger.info("processing for %s orders paid_at in the period %s to %s" % (organization.code, paid_start_date, paid_end_date))
        else:
            # 非期間内有効券の場合はstart_date <= Performance.start_on < end_dateのものを抽出
            # 期間内有効券の場合はstart_date <= Performance.end_on < end_dateのものを抽出
            if start_date:
                query = query.filter(or_(and_(Performance.end_on == None, Performance.start_on >= start_date), and_(Performance.end_on != None, Performance.end_on >= start_date)))
            if end_date:
                query = query.filter(or_(and_(Performance.end_on == None, Performance.start_on < end_date), and_(Performance.end_on != None, Performance.end_on < end_date)))

        orders = query.all()
        logger.info('number of orders to process: %d' % len(orders))
        for order in orders:
            # orgs_not_consider_rakutepayにあるorganizationかつ楽天ペイの予約は対象外
            # orgs_not_consider_rakutenpayは__init__.pyにて設定されます
            if order.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID and organization.code in orgs_not_consider_rakutenpay:
                continue

            point_grant_history_entries_by_type = {}
            for point_grant_history_entry in order.point_grant_history_entries:
                if point_grant_history_entry.edited_by is None: # Skip manual grant mode
                    point_grant_history_entries = point_grant_history_entries_by_type.get(point_grant_history_entry.user_point_account.type)
                    if point_grant_history_entries is None:
                        point_grant_history_entries = point_grant_history_entries_by_type[point_grant_history_entry.user_point_account.type] = []
                    point_grant_history_entries.append(point_grant_history_entry)

            point_by_type = calculate_point_for_order(order)
            user_point_accounts = lookup_user_point_accounts(order=order)
                    
            for type, point in point_by_type.items():
                if user_point_accounts is None:
                    logger.info('Order(order_no=%s): no point account information is associated for point type (%d).' % (order.order_no, type))
                    continue

                for user_point_account in user_point_accounts:
                    if user_point_account.type == type:
                        break
                else:
                    user_point_account = None

                if user_point_account is None:
                    logger.info('Order(order_no=%s): no point account information for point type (%d) is associated to User(id=%r) .' % (order.order_no, type, order.user_id))
                    continue

                if type in point_grant_history_entries_by_type:
                    logger.info('Order(order_no=%s): history already exists for point type (%d).' % (order.order_no, type))
                    continue

                logger.info('granting %s to Order(order_no=%s, created_at=%s).' % (point_by_type[type], order.order_no, order.created_at))
                DBSession.add(PointGrantHistoryEntry(
                    user_point_account=user_point_account,
                    order=order,
                    amount=point_by_type[type],
                    submitted_on=submitted_on
                    ))


        logger.info("end processing orders for Organization(id=%ld)" % organization.id)

    logger.info("end processing for orders whose performance has ended in the period %s to %s" % (start_date, end_date))

def make_point_grant_data():
    import locale
    locale.setlocale(locale.LC_ALL, '')

    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--organization')
    parser.add_argument('-s', '--start-date')
    parser.add_argument('-e', '--end-date')
    parser.add_argument('-d', '--date')
    parser.add_argument('config')
    parser.add_argument('submitted_on')

    args = parser.parse_args()

    start_date = None
    end_date = None

    try:
        submitted_on = parsedatetime(args.submitted_on).date()
    except:
        sys.stderr.write("Invalid date: %s\n" % args.submitted_on)
        sys.stderr.flush()
        sys.exit(255)

    if args.start_date:
        try:
            start_date = parsedatetime(args.start_date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.start_date)
            sys.stderr.flush()
            sys.exit(255)

    if args.end_date:
        try:
            end_date = parsedatetime(args.end_date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.end_date)
            sys.stderr.flush()
            sys.exit(255)

    if args.date:
        if start_date is not None or end_date is not None:
            sys.stderr.write("(--start-date|--end-date) and --date are mutually exclusive")
            sys.exit(255)
        try:
            date = parsedatetime(args.date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.date)
            sys.stderr.flush()
            sys.exit(255)
    else:
        if start_date is None and end_date is None:
            date = todatetime(submitted_on - timedelta(days=3))

    if start_date is None and end_date is None:
        start_date = date
        end_date = date + timedelta(days=1)

    setup_logging(args.config)
    env = bootstrap(args.config)

    transaction.begin()
    try:
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Organization
        organization = None
        if args.organization:
            try:
                organization = DBSession.query(Organization) \
                    .filter(
                        (Organization.name == args.organization) \
                        | (Organization.code == args.organization) \
                        | (Organization.short_name == args.organization) \
                        | (Organization.id == args.organization)
                        ) \
                    .one()
            except:
                sys.stderr.write("no such organization: %s\n" % args.organization)
                sys.stderr.flush()
                sys.exit(255)

        do_make_point_grant_data(
            env['registry'],
            organization,
            start_date,
            end_date,
            submitted_on
            )
        transaction.commit()
    except:
        transaction.abort()
        raise

def do_export_point_grant_data(registry, organization, type, reason_code, shop_name, submitted_on, include_granted_data, encoding):
    from .models import PointGrantHistoryEntry

    # 楽天チケットと一緒にポイント付与の場合は何もしない。
    if organization.code in orgs_with_rakuten:
        logger.info(
            "Exporting point grant data of this organization(id=%ld, name=%s) is executed within Rakuten Ticket. Skipping" % (
            organization.id, organization.name))

    else:
        logger.info("start exporting point granting data scheduled for submission on %s, for Organization(id=%ld)" % (submitted_on, organization.id))

        query = build_export_data_query(organization=organization, submitted_on=submitted_on, type=type)

        if not include_granted_data:
            query = query.filter(PointGrantHistoryEntry.granted_at == None)

        for point_grant_history_entry in query:
            cols = [
                point_grant_history_entry.order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                point_grant_history_entry.user_point_account.account_number,
                reason_code,
                point_grant_history_entry.order.order_no,
                encode_point_grant_history_entry_id(point_grant_history_entry.id),
                unicode(point_grant_history_entry.amount.to_integral()),
                shop_name,
                ''
                ]
            sys.stdout.write(u'\t'.join(cols).encode(encoding))
            sys.stdout.write("\n")

        logger.info("end exporting point granting data scheduled for submission on %s, for Organization(id=%ld)" % (submitted_on, organization.id))

def export_point_grant_data():
    import locale
    locale.setlocale(locale.LC_ALL, '')

    if hasattr(locale, 'nl_langinfo'):
        default_encoding = locale.nl_langinfo(locale.CODESET)
    else:
        default_encoding = 'ascii'

    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--organization', required=True)
    parser.add_argument('-e', '--encoding')
    parser.add_argument('-t', '--type')
    parser.add_argument('-s', '--include-submitted', action='store_true')
    parser.add_argument('-R', '--reason-code', required=True)
    parser.add_argument('-S', '--shop-name', required=True)
    parser.add_argument('config')
    parser.add_argument('submitted_on')

    args = parser.parse_args()

    try:
        submitted_on = parsedatetime(args.submitted_on).date()
    except:
        sys.stderr.write("Invalid date: %s\n" % args.submitted_on)
        sys.stderr.flush()
        sys.exit(255)

    from altair.app.ticketing.users.models import UserPointAccountTypeEnum
    try:
        type = getattr(UserPointAccountTypeEnum, args.type or 'Rakuten').v
    except:
        sys.stderr.write("Invalid point type: %s\n" % args.type)
        sys.stderr.flush()
        sys.exit(255)

    reason_code = args.reason_code.decode(default_encoding)
    shop_name = args.shop_name.decode(default_encoding)

    setup_logging(args.config)
    env = bootstrap(args.config)

    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Organization
    organization = None
    try:
        organization = DBSession.query(Organization) \
            .filter(
                (Organization.name == args.organization) \
                | (Organization.code == args.organization) \
                | (Organization.short_name == args.organization) \
                | (Organization.id == args.organization)
                ) \
            .one()
    except:
        sys.stderr.write("No such organization: %s\n" % args.organization)
        sys.stderr.flush()
        sys.exit(255)

    do_export_point_grant_data(
        env['registry'],
        organization,
        type,
        reason_code,
        shop_name,
        submitted_on,
        args.include_submitted,
        args.encoding or default_encoding
        )

def do_export_refund_point_grant_data(registry, organization, user_point_type, date_number, reason_code, shop_name, refunded_point_at, encoding):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Performance, Event, Organization
    from altair.app.ticketing.users.models import UserPointAccount
    from altair.app.ticketing.orders.models import Order, order_user_point_account_table, RefundPointEntry
    from sqlalchemy.sql.expression import desc
    from sqlalchemy import Date as sql_date, cast as sql_cast
    from dateutil.relativedelta import relativedelta

    # 楽天チケットと一緒にポイント付与の場合は何もしない。
    if organization.code in orgs_with_rakuten:
        logger.info(
            "Exporting refund point grant data of this organization(id=%ld, name=%s) is executed within Rakuten Ticket. Skipping" % (organization.id, organization.name))
        return

    now = datetime.now()
    organization_ids = build_org_id_as_list(organization)  # ここで楽天チケットと一緒に付与するorgがあれば取得する

    # Order_UserPointAccountのorder_idはbranch_no=1のものなので、予約インポートや購入情報更新で論理削除されている可能性がある
    # このためinclude_deleted=Trueとする
    sub_query = \
        DBSession.query(
            order_user_point_account_table.c.user_point_account_id.label('user_point_account_id'),
            Order.order_no.label('order_no'),
            include_deleted=True) \
        .join(Order, Order.id == order_user_point_account_table.c.order_id) \
        .group_by(Order.order_no) \
        .subquery()

    query = DBSession.query(Order, UserPointAccount, RefundPointEntry)\
        .join(Order.performance) \
        .join(Performance.event) \
        .join(sub_query,
              sub_query.c.order_no == Order.order_no) \
        .join(UserPointAccount,
              UserPointAccount.id == sub_query.c.user_point_account_id) \
        .join(RefundPointEntry) \
        .filter(Event.organization_id.in_(organization_ids)) \
        .filter(RefundPointEntry.order_no == Order.order_no) \
        .filter(
                or_(
                    and_(
                        sql_cast(Order.refunded_at, sql_date) == (now + relativedelta(days=date_number)).date(),
                        Order.refunded_at != None,
                        Order.refund_id != None),
                    and_(
                        sql_cast(Order.created_at, sql_date) == (now + relativedelta(days=date_number)).date(),
                        Order.refunded_at == None,
                        Order.refund_id == None)
                    )
                ) \
        .filter(Order.canceled_at == None) \
        .filter(RefundPointEntry.refund_point_amount != 0) \
        .filter(RefundPointEntry.refunded_point_at == None) \
        .filter(UserPointAccount.type == user_point_type)

    logger.info(query)
    results = query.all()
    logger.info('number of orders to process: %d' % len(results))
    for res in results:
        # 払戻予約の場合[Order.refunded_at], インポートの場合[RefundPointEntry.created_at]がポイント発生日になる
        point_grant_date = res.Order.refunded_at if res.Order.refunded_at else res.RefundPointEntry.created_at
        cols = [
            point_grant_date.strftime("%Y-%m-%d %H:%M:%S"),
            res.UserPointAccount.account_number,
            reason_code,
            res.Order.order_no,
            refund_point_grant_history_entry_id(res.RefundPointEntry.id, res.RefundPointEntry.seq_no),
            unicode(res.RefundPointEntry.refund_point_amount.to_integral()),
            shop_name,
            ''
            ]
        refund_point = res.RefundPointEntry
        refund_point.refunded_point_at = refunded_point_at
        refund_point.save()
        sys.stdout.write(u'\t'.join(cols).encode(encoding))
        sys.stdout.write("\n")

def export_refund_point_grant_data():
    import locale
    locale.setlocale(locale.LC_ALL, '')

    if hasattr(locale, 'nl_langinfo'):
        default_encoding = locale.nl_langinfo(locale.CODESET)
    else:
        default_encoding = 'ascii'

    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--organization', required=True)
    parser.add_argument('-e', '--encoding')
    parser.add_argument('-t', '--user-point-type')
    parser.add_argument('-d', '--refund-date-number', required=True)
    parser.add_argument('-R', '--reason-code', required=True)
    parser.add_argument('-S', '--shop-name', required=True)
    parser.add_argument('config')
    parser.add_argument('refunded_point_at')

    args = parser.parse_args()
    try:
        refunded_point_at = parsedatetime(args.refunded_point_at)
    except:
        sys.stderr.write("Invalid date: %s\n" % args.refunded_point_at)
        sys.stderr.flush()
        sys.exit(255)

    from altair.app.ticketing.users.models import UserPointAccountTypeEnum
    try:
        user_point_type = getattr(UserPointAccountTypeEnum, args.user_point_type or 'Rakuten').v
    except:
        sys.stderr.write("Invalid user point type: %s\n" % args.user_point_type)
        sys.stderr.flush()
        sys.exit(255)

    reason_code = args.reason_code.decode(default_encoding)
    shop_name = args.shop_name.decode(default_encoding)

    setup_logging(args.config)
    env = bootstrap(args.config)
    date_number = int(args.refund_date_number)

    transaction.begin()
    try:
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Organization
        organization = None
        try:
            organization = DBSession.query(Organization) \
                .filter(
                    (Organization.name == args.organization) \
                    | (Organization.code == args.organization) \
                    | (Organization.short_name == args.organization) \
                    | (Organization.id == args.organization)
                    ) \
                .one()
        except:
            sys.stderr.write("No such organization: %s\n" % args.organization)
            sys.stderr.flush()

        do_export_refund_point_grant_data(
            env['registry'],
            organization,
            user_point_type,
            date_number,
            reason_code,
            shop_name,
            refunded_point_at,
            args.encoding or default_encoding
        )
        transaction.commit()
    except:
        transaction.abort()
        raise
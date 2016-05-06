# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import logging
import datetime
import traceback
import transaction
import sqlalchemy as sa
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )

from pyramid.decorator import reify
from pyramid.renderers import render_to_response

from altair.augus.types import Status
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser
from altair.augus.protocols import (
    PerformanceSyncRequest,
    TicketSyncRequest,
    DistributionSyncRequest,
    VenueSyncRequest,
    VenueSyncResponse,
    )

from altair.app.ticketing.core.models import (
    Organization,
    AugusAccount,
    AugusPerformance,
    AugusTicket,
    AugusPutback,
    AugusVenue,
    )

from .mails import send_venue_sync_request_mail
from .importers import (
    AugusPerformanceImpoter,
    AugusTicketImpoter,
    AugusDistributionImporter,
    )
from .exporters import (
    AugusExporter,
    AugusDistributionExporter,
    AugusPutbackExporter,
    AugusAchievementExporter,
    )
from .errors import (
    AugusDataImportError,
    IllegalImportDataError,
    )

logger = logging.getLogger(__name__)

class AugusAccountNotFound(Exception):
    pass

def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        pass


class PathManager(object):
    _staging = 'staging'
    _pending = 'pending'

    def __init__(self, augus_account, var_dir=None):
        self._augus_account = augus_account
        self._var_dir = var_dir if var_dir else os.getcwd()
        self.init()

    def init(self):
        for path in (self.send_dir_staging,
                     self.send_dir_pending,
                     self.recv_dir_staging,
                     self.recv_dir_pending,
                     ):
            mkdir_p(path)

    @property
    def work_dir(self):
        return os.path.join(self._var_dir, str(self._augus_account.id))

    @property
    def send_dir_staging(self):
        return os.path.join(self.work_dir, self._augus_account.send_dir.strip('/'), self._staging)

    @property
    def send_dir_pending(self):
        return os.path.join(self.work_dir, self._augus_account.send_dir.strip('/'), self._pending)


    @property
    def recv_dir_staging(self):
        return os.path.join(self.work_dir, self._augus_account.recv_dir.strip('/'), self._staging)

    @property
    def recv_dir_pending(self):
        return os.path.join(self.work_dir, self._augus_account.recv_dir.strip('/'), self._pending)


class AugusWorker(object):
    def __init__(self, augus_account_id, var_dir=None):
        self._augus_account_id = int(augus_account_id) # need integer
        self._var_dir = var_dir if var_dir else os.getcwd()

    @reify
    def path(self):
        return PathManager(self.augus_account, self._var_dir)

    @reify
    def augus_account(self):
        try:
            augus_account = AugusAccount\
                .query\
                .filter(AugusAccount.id==self._augus_account_id)\
                .one()
            from sqlalchemy.orm.session import make_transient
            make_transient(augus_account)
        except (NoResultFound, MultipleResultsFound) as err:
            raise AugusAccountNotFound('AugusAccount.id={}'.format(self._augus_account_id))
        else:
            return augus_account

    def get_transporter(self):
        transporter = FTPTransporter(
            hostname=self.augus_account.host,
            username=self.augus_account.username,
            password=self.augus_account.password,
            # passive=True, # 暫定的にactiveで接続するようにする
            )
        return transporter

    def download(self, remove=True):
        staging = self.path.recv_dir_staging

        transporter = self.get_transporter()
        transporter.chdir(self.augus_account.recv_dir)
        for name in transporter.listdir():
            if AugusParser.is_protocol(name):
                src = name
                dst = os.path.join(staging, name)
                transporter.get(src, dst, remove=remove)

    def upload(self):
        staging = self.path.send_dir_staging

        transporter = self.get_transporter()
        transporter.chdir(self.augus_account.send_dir)
        for name in os.listdir(staging):
            logger.info('target: {}'.format(name))
            if AugusParser.is_protocol(name):
                src = os.path.join(staging, name)
                dst = name
                logger.info('start upload: {} -> {}'.format(src, dst))
                transporter.put(src, dst)

                pending_file = os.path.join(self.path.send_dir_pending, name)
                logger.info('start pending: {} -> {}'.format(src, pending_file))
                shutil.move(src, pending_file) # pending
                logger.info('finished')

    def performancing(self):
        staging = self.path.recv_dir_staging
        pending = self.path.recv_dir_pending
        target = PerformanceSyncRequest
        importer = AugusPerformanceImpoter()

        paths = []
        ids = []

        for name in filter(target.match_name, os.listdir(staging)):
            path = os.path.join(staging, name)
            paths.append(path)

            request = AugusParser.parse(path)
            entries = importer.import_(request, self.augus_account)
            ids.extend(entry.id for entry in entries)

        transaction.commit() # commit
        for path in paths:
            shutil.move(path, pending)
        return ids

    def ticketing(self):
        staging = self.path.recv_dir_staging
        pending = self.path.recv_dir_pending
        target = TicketSyncRequest
        importer = AugusTicketImpoter()

        paths = []
        ids = []

        for name in filter(target.match_name, os.listdir(staging)):
            path = os.path.join(staging, name)
            paths.append(path)

            request = AugusParser.parse(path)
            entries = importer.import_(request, self.augus_account)
            ids.extend(entry.id for entry in entries)

        transaction.commit() # commit
        for path in paths:
            shutil.move(path, pending)
        return ids

    def distribute(self, sleep=1.5):
        logger.info('start augus distribition: augus_account_id={}'.format(self.augus_account.id))
        staging = self.path.recv_dir_staging
        pending = self.path.recv_dir_pending
        send_dir_staging = self.path.send_dir_staging
        target = DistributionSyncRequest
        importer = AugusDistributionImporter()
        exporter = AugusDistributionExporter()
        status = Status.NG

        successes = []
        errors = []
        not_yets = []
        exception = None

        try:
            for name in filter(target.match_name, os.listdir(staging)):
                logger.info('Target file: {}'.format(name))
                path = os.path.join(staging, name)

                request = AugusParser.parse(path)

                try:
                    importer.import_(request, self.augus_account)
                    status = Status.OK
                    logger.info('Success')
                except AugusDataImportError as err: # 未連携状態の可能性->次のターンで再試行
                    transaction.abort()
                    not_yets.append(request)
                    logger.info('Cooperation has not been completed: {}'.format(err))
                    continue
                except IllegalImportDataError as err: # 座席不正など -> Augus側にエラー通知
                    logger.info('Illigal error: {}'.format(err))
                    pass
                except Exception as err: # 未知のエラーはそのまま上位に送出
                    transaction.abort()
                    logger.info('Unknown error: {}'.format(err))
                    raise

                try:
                    time.sleep(sleep)
                    logger.info('Exporting start')
                    exporter.export(send_dir_staging, request, status)
                    logger.info('Exporting done')
                    shutil.move(path, pending)
                    logger.info('Move file done')
                except Exception as err:
                    logger.info('Error: {}'.format(err))
                    transaction.abort()
                    raise
                else:
                    if status == Status.OK:
                        logger.info('Data commit')
                        transaction.commit()
                        successes.append(request)
                    else:
                        transaction.abort()
                        errors.append(request)
                        logger.info('Not able to seat distribution')
                        raise
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            exception = err
        return successes, errors, not_yets, exception

    def putback(self):
        logger.info('start augus putback: augus_account_id={}'.format(self.augus_account.id))
        staging = self.path.send_dir_staging

        exporter = AugusPutbackExporter()
        putback_codes = []
        try:
            responses = exporter.export(staging, self.augus_account.code)
            putback_codes = [res[0].putback_code for res in responses if len(res)]
        except AugusDataImportError as err:
            logger.error('Augus putback failed: {}'.format(err))
            transaction.abort()
            raise
        except Exception as err:
            logger.error('Augus putback failed (unknown error): {}'.format(err))
            transaction.abort()
            raise
        else:
            transaction.commit()
        return putback_codes

    def achieve(self, all_=False, sleep=1.5):
        logger.info('start augus distribition: augus_account_id={}'.format(self.augus_account.id))
        staging = self.path.send_dir_staging
        exporter = AugusAchievementExporter()
        now = datetime.datetime.now()
        moratorium = datetime.timedelta(days=90)
        qs = AugusPerformance\
          .query\
          .filter(AugusPerformance.augus_account_id==self.augus_account.id) \
          .filter(AugusPerformance.start_on >= now - moratorium)

        if not all_:
            qs = qs.filter(AugusPerformance.is_report_target==True)
        else:
            qs = qs.filter(AugusPerformance.stoped_at==None)

        ag_performances = qs.all()
        ids = [ag_performance.id for ag_performance in ag_performances]
        for ag_performance in ag_performances:
            time.sleep(sleep)
            logger.info('Achievement export start: AugusPerformance.id={}'.format(ag_performance.id))
            res = exporter.export_from_augus_performance(ag_performance)
            res.customer_id = self.augus_account.code
            path = os.path.join(staging, res.name)
            logger.info('export: {}'.format(path))
            AugusExporter.export(res, path)
            ag_performance.is_report_target = False
            ag_performance.save()
        transaction.commit()
        return ids


    def venue_sync_request(self, mailer, sleep=2):
        logger.info('start augus venue sync request: augus_account_id={}'.format(self.augus_account.id))
        staging = self.path.recv_dir_staging
        pending = self.path.recv_dir_pending

        target = VenueSyncRequest
        for name in filter(target.match_name, os.listdir(staging)):
            time.sleep(sleep)
            path = os.path.join(staging, name)
            logger.info('Venue sync request: target: {}'.format(path))
            send_venue_sync_request_mail(mailer, self.augus_account, path)
            logger.info('Venue sync request: send mail: {}'.format(path))
            shutil.move(path, pending) # pending
            logger.info('Venue sync request: ok: {}'.format(path))


    def _sync_response_target_augus_venues(self):
        """会場図連携完了通知対象AugusVenueを取得する

        対象の条件は次の通り

        - 連携完了通知予約中のものの内、次のいずれかの条件を満たす

          - 未通知
          - 通知日時よりあとに通知予約がされている

        """
        return AugusVenue\
          .query\
          .filter(AugusVenue.augus_account_id==self.augus_account.id)\
          .filter(AugusVenue.reserved_at!=None)\
          .filter(sa.or_(AugusVenue.notified_at==None,
                         sa.and_(AugusVenue.notified_at!=None,
                                 AugusVenue.reserved_at>AugusVenue.notified_at)))



    def venue_sync_response(self):
        logger.info('start augus venue sync response: augus_account_id={}'.format(self.augus_account.id))
        ids = []
        staging = self.path.send_dir_staging
        augus_venues = self._sync_response_target_augus_venues()
        now = datetime.datetime.now()
        for augus_venue in augus_venues:
            ids.append(augus_venue.id)
            venue_response = VenueSyncResponse(
                customer_id=self.augus_account.code, venue_code=augus_venue.code)
            record = venue_response.record()
            record.venue_code = augus_venue.code
            record.venue_name = augus_venue.name
            record.status = Status.OK.value
            record.venue_version = augus_venue.version
            venue_response.append(record)

            path = os.path.join(staging, venue_response.name)
            AugusExporter.export(venue_response, path)
            augus_venue.notified_at = now
            augus_venue.save()
            transaction.commit()
        return ids


class AugusOperationManager(object):
    def __init__(self, organization_ids=[], var_dir=None):
        self._organization_ids = map(int, organization_ids)
        self._var_dir = var_dir if var_dir else os.getcwd()

    def augus_accounts(self):
        qs = Organization.query
        if self._organization_ids:
            qs = qs.filter(Organization.id.in_(self._organization_ids))
        organizations = qs.all()

        augus_account_ids = [
            account.augus_account.id
            for organization in organizations
            for account in organization.accounts
            if account.augus_account
            ]

        for augus_account_id in augus_account_ids:
            yield AugusAccount.query.filter(AugusAccount.id==augus_account_id).one()

    def augus_workers(self):
        for augus_account in self.augus_accounts():
            worker = AugusWorker(augus_account.id, var_dir=self._var_dir)
            yield worker

    def send_mail(self, mailer, augus_account, subject, template_path, params):
        sender = 'dev@ticketstar.jp'
        recipient = 'ticket-op@mail.rakuten.com' # augus_account.email
        body = render_to_response(template_path, params)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body.text,
            )
        mailer.send(sender, [recipient])

    def download(self):
        for worker in self.augus_workers():
            worker.download()


    def upload(self):
        for worker in self.augus_workers():
            worker.upload()


    def performancing(self, mailer=None):
        for worker in self.augus_workers():
            augus_account = worker.augus_account
            try:
                ids = worker.performancing()
            except:
                transaction.abort()
                raise

            if mailer and len(ids):
                augus_performances = AugusPerformance\
                  .query\
                  .filter(AugusPerformance.id.in_(ids))\
                  .all()
                params = {
                    'augus_performances': augus_performances,
                    }
                self.send_mail(
                    mailer, augus_account,
                    u'【オーガス連携】公演連携のおしらせ',
                    'altair.app.ticketing:templates/cooperation/augus/mails/augus_performance.html',
                    params,
                    )


    def ticketing(self, mailer=None):
        for worker in self.augus_workers():
            augus_account = worker.augus_account
            try:
                ids = worker.ticketing()
            except:
                transaction.abort()
                raise
            if mailer and len(ids):
                augus_performances = AugusPerformance\
                  .query\
                  .join(AugusTicket)\
                  .filter(AugusTicket.id.in_(ids))\
                  .all()
                params = {
                    'augus_performances': augus_performances,
                    'count': len(ids),
                    }
                self.send_mail(
                    mailer, augus_account,
                    u'【オーガス連携】チケット連携のおしらせ',
                    'altair.app.ticketing:templates/cooperation/augus/mails/augus_ticket.html',
                    params,
                    )


    def distribute(self, mailer=None):
        for worker in self.augus_workers():
            augus_account = worker.augus_account
            try:
                successes, errors, not_yets, exception = worker.distribute()
            except:
                transaction.abort()
                raise
            if mailer and (successes or errors or not_yets):
                mailer.successes = successes
                mailer.errors = errors
                mailer.not_yets = not_yets
                recipients = ['ticket-op@mail.rakuten.com'] # augus_account.email
                sender = 'dev@ticketstar.jp'
                mailer.send(recipients, sender)
            if exception:
                raise exception

    def putback(self, mailer):
        for worker in self.augus_workers():
            augus_account = worker.augus_account
            augus_account_code = augus_account.code
            try:
                putback_codes = worker.putback()
            except:
                raise

            if mailer and len(putback_codes):
                augus_putbacks = AugusPutback\
                    .query\
                    .filter(AugusPutback.augus_putback_code.in_(putback_codes))\
                    .filter(AugusAccount.code==augus_account_code)\
                    .all()

                params = {
                    'augus_putbacks': augus_putbacks,
                    }

                self.send_mail(
                    mailer, augus_account,
                    u'【オーガス連携】返券のおしらせ',
                    'altair.app.ticketing:templates/cooperation/augus/mails/augus_putback.html',
                    params,
                    )


    def achieve(self, mailer, all_=False):
        for worker in self.augus_workers():
            augus_account_id = worker.augus_account.id
            ids = []
            try:
                ids = worker.achieve(all_)
            except:
                raise

            if mailer and len(ids):
                augus_performances = AugusPerformance\
                    .query\
                    .filter(AugusPerformance.id.in_(ids))\
                    .filter(AugusPerformance.augus_account_id==augus_account_id)\
                    .all()

                params = {
                    'augus_performances': augus_performances,
                    }

                self.send_mail(
                    mailer, worker.augus_account,
                    u'【オーガス連携】販売実績通知のおしらせ',
                    'altair.app.ticketing:templates/cooperation/augus/mails/augus_achievement.html',
                    params,
                    )

    def venue_sync_request(self, mailer=None):
        for worker in self.augus_workers():
            try:
                worker.venue_sync_request(mailer)
            except:
                raise

    def venue_sync_response(self, mailer=None):
        for worker in self.augus_workers():
            augus_account_id = worker.augus_account.id
            ids = []
            try:
                ids = worker.venue_sync_response()
            except:
                raise

            if mailer and len(ids):
                augus_venues = AugusVenue\
                  .query\
                  .filter(AugusVenue.id.in_(ids))
                params = {
                    'augus_venues': augus_venues,
                    }

                self.send_mail(
                    mailer, worker.augus_account,
                    u'【オーガス連携】会場連携完了通知のおしらせ',
                    'altair.app.ticketing:templates/cooperation/augus/mails/augus_venue_sync_response.html',
                    params,
                    )

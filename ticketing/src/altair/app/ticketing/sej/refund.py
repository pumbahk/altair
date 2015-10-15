# encoding: utf-8 
from __future__ import absolute_import

import os
import logging
import csv
import codecs
import zipfile
import re
import shutil
from collections import namedtuple
from datetime import date, time, datetime, timedelta
from urlparse import urlparse
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.orm import contains_eager, joinedload

from .api import get_nwts_uploader_factory
from .zip_file import EnhZipFile
from .models import SejRefundTicket, SejRefundEvent

logger = logging.getLogger(__name__)

NWTSInfo = namedtuple('NWTSInfo', (
    'nwts_endpoint_url',
    'nwts_terminal_id',
    'nwts_password',
    ))

class SejRefundFileManager(object):
    def __init__(self, stage_dir, sent_dir, pending_dir):
        self.stage_dir = stage_dir
        self.sent_dir = sent_dir
        self.pending_dir = pending_dir

    def get_new_stage_dir_for(self, now):
        work_dir = os.path.join(self.stage_dir, now.strftime("%Y%m%d"))
        def make_room(dir_, serial=0):
            if os.path.exists(dir_):
                next_dir = '%s.%d' % (work_dir, serial)
                make_room(next_dir, serial + 1)
                os.rename(dir_, next_dir)
        make_room(work_dir)
        os.mkdir(work_dir)
        return work_dir

    def get_latest_stage_dir(self, now):
        work_dir = os.path.join(self.stage_dir, now.strftime("%Y%m%d"))
        if not os.path.exists(work_dir):
            return None
        return work_dir

    def mark_file_sent(self, p):
        if not p.startswith(self.stage_dir):
            raise ValueError("specified file (%s) does not exist under %s" % (p, self.stage_dir))
        vpart = os.path.dirname(p[len(self.stage_dir):]).lstrip('/')
        sent_dir = os.path.join(self.sent_dir, vpart)
        if not os.path.exists(sent_dir):
            os.makedirs(sent_dir)
        os.rename(p, os.path.join(sent_dir, os.path.basename(p)))

    def mark_file_pending(self, p):
        if not p.startswith(self.stage_dir):
            raise ValueError("specified file (%s) does not exist under %s" % (p, self.stage_dir))
        vpart = os.path.dirname(p[len(self.stage_dir):]).lstrip('/')
        pending_dir = os.path.join(self.pending_dir, vpart)
        if not os.path.exists(pending_dir):
            os.makedirs(pending_dir)
        os.rename(p, os.path.join(pending_dir, os.path.basename(p)))

def create_refund_file_manager_from_settings(settings):
    stage_dir = settings['altair.sej.refund.stage_dir']
    sent_dir = settings['altair.sej.refund.sent_dir']
    pending_dir = settings['altair.sej.refund.pending_dir']
    return SejRefundFileManager(
        stage_dir=stage_dir,
        sent_dir=sent_dir,
        pending_dir=pending_dir
        )

class SejRefundRecordProvider(object):
    def __init__(self, target_date, session):
        self._refund_events = None
        self._refund_tickets = None
        self._nwts_info_list = None
        self.target_date = target_date
        self.target_from = datetime.combine(target_date + timedelta(days=-1), time(6,0))
        self.target_to = datetime.combine(target_date, time(6,0))
        self.session = session
   
    def _populate_refund_events(self):
        if self._refund_events is not None:
            return
        refund_events = {}
        query = self.session.query(SejRefundEvent) \
            .join(SejRefundTicket) \
            .filter(self.target_date <= SejRefundEvent.end_at)
        for refund_event in query.distinct():
            nwts_info = NWTSInfo(
                nwts_endpoint_url=refund_event.nwts_endpoint_url,
                nwts_terminal_id=refund_event.nwts_terminal_id,
                nwts_password=refund_event.nwts_password
                )
            refund_events.setdefault(nwts_info, []).append(refund_event)
        self._refund_events = refund_events

    def _populate_refund_tickets(self):
        if self._refund_tickets is not None:
            return
        refund_tickets = {}
        query = self.session.query(SejRefundTicket) \
            .options(joinedload(SejRefundTicket.refund_event)) \
            .filter(
                or_(
                    SejRefundTicket.sent_at == None,
                    and_(
                        self.target_from <= SejRefundTicket.sent_at,
                        SejRefundTicket.sent_at < self.target_to
                        )
                    )
                )
        for refund_ticket in query:
            refund_event = refund_ticket.refund_event
            nwts_info = NWTSInfo(
                nwts_endpoint_url=refund_event.nwts_endpoint_url,
                nwts_terminal_id=refund_event.nwts_terminal_id,
                nwts_password=refund_event.nwts_password
                )
            refund_tickets.setdefault(nwts_info, []).append(refund_ticket)
        self._refund_tickets = refund_tickets

    @property
    def nwts_info_list(self):
        self._populate_refund_events()
        self._populate_refund_tickets()
        keys = self._refund_events.viewkeys()
        assert keys >= self._refund_tickets.viewkeys()
        return keys

    def get_refund_events_for(self, nwts_info):
        self._populate_refund_events()
        return self._refund_events.get(nwts_info, [])

    def get_refund_tickets_for(self, nwts_info):
        return self._refund_tickets.get(nwts_info, [])

def encode_to_sjis(row):
    encoded = []
    for value in row:
        if value:
            if not isinstance(value, unicode):
                value = unicode(value)
            value = value.encode('shift_jis')
        else:
            value = ''
        encoded.append(value)
    return encoded

class SejRefundZipFileBuilder(object):
    def __init__(self, target_date, work_dir):
        self.work_dir = work_dir
        target_ymd = target_date.strftime('%Y%m%d')
        self.zip_file_name = '%s.zip' % target_ymd
        self.archive_file_name = 'archive.txt'
        self.refund_event_file_name = target_ymd + '_TPBKOEN.dat'
        self.refund_ticket_file_name = target_ymd + '_TPBTICKET.dat'

    def _create_refund_event_file(self, sej_refund_events, now):
        # SejRefundEvent -> yyyymmdd_tpbkoen.dat
        refund_event_file_path = os.path.join(self.work_dir, self.refund_event_file_name)
        refund_event_tsv = open(refund_event_file_path, 'w')
        tsv_writer = csv.writer(refund_event_tsv, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n')
        try:
            for sej_refund_event in sej_refund_events:
                tsv_writer.writerow(encode_to_sjis([
                    sej_refund_event.available,
                    sej_refund_event.shop_id,
                    sej_refund_event.event_code_01,
                    sej_refund_event.event_code_02,
                    sej_refund_event.title,
                    sej_refund_event.sub_title,
                    sej_refund_event.event_at.strftime('%Y%m%d'),
                    sej_refund_event.start_at.strftime('%Y%m%d'),
                    sej_refund_event.end_at.strftime('%Y%m%d'),
                    sej_refund_event.event_expire_at.strftime('%Y%m%d'),
                    sej_refund_event.ticket_expire_at.strftime('%Y%m%d'),
                    sej_refund_event.refund_enabled,
                    sej_refund_event.disapproval_reason,
                    unicode(sej_refund_event.need_stub),
                    sej_refund_event.remarks,
                    sej_refund_event.un_use_01,
                    sej_refund_event.un_use_02,
                    sej_refund_event.un_use_03,
                    sej_refund_event.un_use_04,
                    sej_refund_event.un_use_05
                    ]))
                sej_refund_event.sent_at = now
        finally:
            refund_event_tsv.close()

        return refund_event_file_path

    def _create_refund_ticket_file(self, sej_refund_tickets, now):
        # SejRefundTicket -> yyyymmdd_tpbticket.dat
        refund_ticket_file_path = os.path.join(self.work_dir, self.refund_ticket_file_name)
        refund_ticket_tsv = open(refund_ticket_file_path, 'w')
        tsv_writer = csv.writer(refund_ticket_tsv, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n')
        try:
            for sej_refund_ticket in sej_refund_tickets:
                tsv_writer.writerow(encode_to_sjis([
                    sej_refund_ticket.available,
                    sej_refund_ticket.refund_event.shop_id,
                    sej_refund_ticket.event_code_01,
                    sej_refund_ticket.event_code_02,
                    sej_refund_ticket.order_no,
                    sej_refund_ticket.ticket_barcode_number,
                    int(sej_refund_ticket.refund_ticket_amount),
                    int(sej_refund_ticket.refund_other_amount)
                    ]))
                sej_refund_ticket.sent_at = now
        finally:
            refund_ticket_tsv.close()
        return refund_ticket_file_path

    def _create_archive_txt(self):
        # archive.txt
        archive_txt_file_path = os.path.join(self.work_dir, self.archive_file_name)
        archive_txt = codecs.open(archive_txt_file_path, 'w', 'shift_jis')
        try:
            archive_txt.write(self.refund_event_file_name + '\r\n')
            archive_txt.write(self.refund_ticket_file_name + '\r\n')
        finally:
            archive_txt.close()
        return archive_txt_file_path

    def __call__(self, zip_file_base, sej_refund_events, sej_refund_tickets, now):
        refund_event_file_path = self._create_refund_event_file(sej_refund_events, now)
        refund_ticket_file_path = self._create_refund_ticket_file(sej_refund_tickets, now)
        archive_txt_file_path = self._create_archive_txt()
        zip_file_path = os.path.join(zip_file_base, self.zip_file_name)
        # create zip file
        zf = EnhZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        zf.append_file(archive_txt_file_path, self.archive_file_name)
        zf.append_file(refund_event_file_path, self.refund_event_file_name)
        zf.append_file(refund_ticket_file_path, self.refund_ticket_file_name)
        zf.close()
        return zip_file_path

def sanitize(n):
    return re.sub(r'[^0-9a-zA-Z_.-]', '-', n)

def build_dirname_from_nwts_info(nwts_info):
    endpoint = urlparse(nwts_info.nwts_endpoint_url)
    return "%s-%s-%s-%s" % (
        sanitize(endpoint.netloc),
        sanitize(endpoint.path),
        sanitize(nwts_info.nwts_terminal_id),
        sanitize(nwts_info.nwts_password),
        )


def calculate_target_date(now):
    # 0:00-5:59の間なら当日, それ以外は翌日でファイル名を生成する
    hour = now.hour
    if hour < 6:
        target_date = now.date()
    else:
        target_date = (now + timedelta(days=1)).date()
    return target_date

def create_refund_zip_files_ex(now=None, target_date=None, work_dir_base='/tmp', session=None):
    if session is None:
        from .models import _session
        session = _session
    if now is None:
        now = datetime.now()
    if target_date is None:
        target_date = now
    provider = SejRefundRecordProvider(
        target_date=target_date,
        session=session
        )

    zip_file_path_list = []
    work_dir_list = []
    try:
        for nwts_info in provider.nwts_info_list:
            work_dir = os.path.join(
                work_dir_base,
                build_dirname_from_nwts_info(nwts_info)
                )
            os.mkdir(work_dir)
            work_dir_list.append(work_dir)
            builder = SejRefundZipFileBuilder(
                target_date=target_date,
                work_dir=work_dir,
                )
            sej_refund_events = provider.get_refund_events_for(nwts_info)
            sej_refund_tickets = provider.get_refund_tickets_for(nwts_info)
            zip_file_path = builder(
                zip_file_base=work_dir,
                sej_refund_events=sej_refund_events,
                sej_refund_tickets=sej_refund_tickets,
                now=now)
            zip_file_path_list.append(zip_file_path)
    except:
        for work_dir in work_dir_list:
            try:
                logger.info("removing %s..." % work_dir)
                shutil.rmtree(work_dir)
            except:
                logger.exception("ignored exception")
        raise

    return zip_file_path_list

def create_refund_zip_files(now=None, work_dir_base='/tmp', session=None):
    target_date = calculate_target_date(now)
    return create_refund_zip_files_ex(session=session, target_date=target_date, now=now, work_dir_base=work_dir_base)

def stage_refund_zip_files(registry, now):
    # sej払戻ファイル生成
    manager = create_refund_file_manager_from_settings(registry.settings)
    work_dir_base = manager.get_new_stage_dir_for(now)
    logger.info("writing refund zip file(s) to %s..." % work_dir_base)
    from .models import _session as sej_session
    try:
        target_date = calculate_target_date(now)
        zip_files = create_refund_zip_files_ex(session=sej_session, target_date=target_date, now=now, work_dir_base=work_dir_base)
        for zip_file in zip_files:
            logger.info("refund zip file successfully created as %s" % zip_file)
    except:
        sej_session.rollback()
        raise
    sej_session.commit()

def send_refund_file(registry, nwts_info, zip_file_path):
    factory = get_nwts_uploader_factory(registry)
    uploader = factory(
        endpoint_url=nwts_info.nwts_endpoint_url,
        terminal_id=nwts_info.nwts_terminal_id,
        password=nwts_info.nwts_password
        )
    uploader(
        application='tpayback.asp',
        file_id='SEIT020U',
        data=open(zip_file_path).read(),
        )

def send_refund_files(registry, now):
    manager = create_refund_file_manager_from_settings(registry.settings)
    work_dir_base = manager.get_latest_stage_dir(now)
    logger.info("sending refund zip file(s) under %s..." % work_dir_base)
    target_date = calculate_target_date(now)
    from .models import _session as sej_session
    provider = SejRefundRecordProvider(
        target_date=target_date,
        session=sej_session
        )
    # preflight
    nwts_info_dir_triplets = []
    for nwts_info in provider.nwts_info_list:
        work_dir = os.path.join(
            work_dir_base,
            build_dirname_from_nwts_info(nwts_info)
            )
        if not os.path.exists(work_dir):
            raise Exception('%s does not exist' % work_dir)
        zip_files = []
        for f in os.listdir(work_dir):
            zip_file = os.path.join(work_dir, f)
            if f.endswith('.zip') and os.path.isfile(zip_file):
                zip_files.append(zip_file)
        if len(zip_files) == 0:
            logger.warning('no zip file exists under %s. skipped.' % work_dir)
            continue
        elif len(zip_files) > 1:
            raise Exception('more than one zip files exist under %s' % work_dir)
        nwts_info_dir_triplets.append((nwts_info, work_dir, zip_files[0]))

    # do it
    for nwts_info, _, zip_file in nwts_info_dir_triplets:
        logger.info("sending {0} to {1.nwts_endpoint_url} (terminal_id={1.nwts_terminal_id})...".format(zip_file, nwts_info))
        try:
            send_refund_file(registry, nwts_info, zip_file)
            manager.mark_file_sent(zip_file)
        except:
            logger.error("failed to send {0} to {1.nwts_endpoint_url} (terminal_id={1.nwts_terminal_id})...".format(zip_file, nwts_info), exc_info=True)
            manager.mark_file_pending(zip_file)

# -*- coding:utf-8 -*-

import codecs
import csv
import re
import os
from datetime import date, time, datetime, timedelta
from lxml import etree
import zipfile

from sqlalchemy.sql.expression import and_, or_

from .models import SejTicketTemplateFile, SejRefundTicket, SejRefundEvent
from .zip_file import EnhZipFile, ZipInfo

MAX_TICKET_DATA_LENGTH = 5000

class SejTicketDataXml(object):
    xml = ''

    def __init__(self, xml):
        self.xml = xml

    def validate(self):
        return len(unicode(self).encode('CP932')) < MAX_TICKET_DATA_LENGTH

    def __unicode__(self):
        from cStringIO import StringIO
        s = StringIO(self.xml.encode('utf8'))
        x = etree.parse(s)
        xml =  re.sub(
            r'''(<\?xml[^>]*)encoding=(?:'[^']*'|"[^"]"|[^> ?]*)\?>''',
            r"\1encoding='Shift_JIS' ?>", etree.tostring(x, encoding='UTF-8', xml_declaration=True))
        return xml.decode("utf-8")

def package_ticket_template_to_zip(session, template_id, shop_id = u'30520', now=None):
    if now is None:
        now = datetime.now()
    sej_tickets = session.query(SejTicketTemplateFile).filter_by(deleted_at = None).all()

    archive_txt_buffer = list()
    csv_text_buffer = list()

    archive_txt_buffer.append("TTEMPLATE.CSV")
    for sej_ticket in sej_tickets:
        if sej_ticket.ticket_html:
            archive_txt_buffer.append("%s/%s.htm" % (template_id, template_id))
        if sej_ticket.ticket_css:
            archive_txt_buffer.append("%s/%s.css" % (template_id, template_id))
        sej_ticket.sent_at = now
        csv_text_buffer.append(','.join([
            sej_ticket.status,
            shop_id,
            sej_ticket.template_id,
            sej_ticket.publish_start_date.strftime('%Y%m%d'),
            sej_ticket.publish_end_date.strftime('%Y%m%d') if sej_ticket.publish_end_date else '99999999',
            sej_ticket.template_name
        ]))

    archive_txt_body = "\r\n".join(archive_txt_buffer) + "\r\n"
    csv_text_body = "\r\n".join(csv_text_buffer) + "\r\n"

    zip_file_name = "/tmp/%s.zip" % template_id
    zf = EnhZipFile(zip_file_name, 'w')

    #

    zi = ZipInfo('archive.txt', now.timetuple()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(archive_txt_body)
    w.close()
    zf.finish_entry()

    zi = ZipInfo('TTEMPLATE.CSV', now.timetuple()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(csv_text_body.encode('sjis'))
    w.close()
    zf.finish_entry()

    for sej_ticket in sej_tickets:
        if sej_ticket.ticket_html:
            zi = ZipInfo("%s/%s.htm" % (template_id, template_id), now.timetuple()[:6])
            zi.external_attr = 0666 << 16L
            w = zf.start_entry(zi)
            w.write(sej_ticket.ticket_html)
            w.close()
            zf.finish_entry()

        if sej_ticket.ticket_css:
            zi = ZipInfo("%s/%s.css" % (template_id, template_id), now.timetuple()[:6])
            zi.external_attr = 0666 << 16L
            w = zf.start_entry(zi)
            w.write(sej_ticket.ticket_css)
            w.close()
            zf.finish_entry()

    zf.close()

    # TODO SEND
    return zip_file_name

def create_refund_zip_file(session, now=None, work_dir='/tmp'):
    if now is None:
        now = datetime.now()
    hour = now.hour
    if hour < 6:
        target_date = now.date()
    else:
        target_date = (now + timedelta(days=1)).date()
    target_ymd = target_date.strftime('%Y%m%d')
    target_from = datetime.combine(target_date + timedelta(days=-1), time(6,0))
    target_to = datetime.combine(target_date, time(6,0))

    # 0:00-5:59の間なら当日, それ以外は翌日でファイル名を生成する
    zip_file_name = '%s.zip' % target_ymd
    archive_file_name = 'archive.txt'
    refund_event_file_name = target_ymd + '_TPBKOEN.dat'
    refund_ticket_file_name = target_ymd + '_TPBTICKET.dat'

    # archive.txt
    archive_txt_file_path = os.path.join(work_dir, archive_file_name)
    archive_txt = codecs.open(archive_txt_file_path, 'w', 'shift_jis')
    archive_txt.write(refund_event_file_name + '\r\n')
    archive_txt.write(refund_ticket_file_name + '\r\n')
    archive_txt.close()

    # SejRefundTicket -> YYYYMMDD_TPBTICKET.dat
    refund_ticket_file_path = os.path.join(work_dir, refund_ticket_file_name)
    refund_ticket_tsv = open(refund_ticket_file_path, 'w')
    tsv_writer = csv.writer(refund_ticket_tsv, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n')
    query = session.query(SejRefundTicket).filter(or_(
        SejRefundTicket.sent_at==None,
        and_(target_from<=SejRefundTicket.sent_at, SejRefundTicket.sent_at<target_to)
        ))
    sej_refund_tickets = query.all()

    refund_event_ids = []
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
        if sej_refund_ticket.refund_event_id not in refund_event_ids:
            refund_event_ids.append(sej_refund_ticket.refund_event_id)
    refund_ticket_tsv.close()

    # SejRefundEvent -> YYYYMMDD_TPBKOEN.dat
    refund_event_file_path = os.path.join(work_dir, refund_event_file_name)
    refund_event_tsv = open(refund_event_file_path, 'w')
    tsv_writer = csv.writer(refund_event_tsv, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n')
    query = session.query(SejRefundEvent)
    if len(refund_event_ids) > 0:
        query = query.filter(or_(SejRefundEvent.id.in_(refund_event_ids), target_date<=SejRefundEvent.end_at))
    else:
        query = query.filter(target_date<=SejRefundEvent.end_at)
    sej_refund_events = query.all()
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
            sej_refund_event.need_stub,
            sej_refund_event.remarks,
            sej_refund_event.un_use_01,
            sej_refund_event.un_use_02,
            sej_refund_event.un_use_03,
            sej_refund_event.un_use_04,
            sej_refund_event.un_use_05
            ]))
        sej_refund_event.sent_at = now
    refund_event_tsv.close()

    if not sej_refund_events:
        return None

    # create zip file
    zip_file_path = os.path.join(work_dir, zip_file_name)
    zf = EnhZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    zf.append_file(archive_txt_file_path, archive_file_name)
    zf.append_file(refund_event_file_path, refund_event_file_name)
    zf.append_file(refund_ticket_file_path, refund_ticket_file_name)
    zf.close()

    return zip_file_path

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

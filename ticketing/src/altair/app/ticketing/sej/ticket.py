# -*- coding:utf-8 -*-

from __future__ import absolute_import

import csv
import re
import os
from datetime import date, time, datetime, timedelta
from lxml import etree

from .models import SejTicketTemplateFile
from zipfile import ZipInfo
from .zip_file import EnhZipFile

MAX_TICKET_DATA_LENGTH = 5000

class TicketDataLargeError(Exception):
    pass

class SejTicketDataXml(object):
    xml = ''

    def __init__(self, xml):
        self.xml = xml

    def validate(self):
        if len(unicode(self).encode('CP932')) > MAX_TICKET_DATA_LENGTH:
            raise TicketDataLargeError

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


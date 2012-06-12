# -*- coding:utf-8 -*-
import datetime

from .zip_file import EnhZipFile, ZipInfo
from .models import SejTicketTemplateFile

import time

import sqlahelper
DBSession = sqlahelper.get_session()

def package_ticket_template_to_zip(template_id,
                                   shop_id = u'30520'):

    sej_tickets = SejTicketTemplateFile.query.filter_by(deleted_at = None).all()

    archive_txt_buffer = list()
    csv_text_buffer = list()

    archive_txt_buffer.append("TTEMPLATE.CSV")
    for sej_ticket in sej_tickets:
        if sej_ticket.ticket_html:
            archive_txt_buffer.append("%s/%s.html" % (template_id, template_id))
        if sej_ticket.ticket_css:
            archive_txt_buffer.append("%s/%s.css" % (template_id, template_id))
        sej_ticket.send_at = datetime.datetime.now()
        print sej_ticket.template_name
        csv_text_buffer.append(','.join([
            sej_ticket.status,
            shop_id,
            sej_ticket.template_id,
            sej_ticket.publish_start_date.strftime('%Y%m%d'),
            sej_ticket.publish_end_date.strftime('%Y%m%d') if sej_ticket.publish_end_date else '99999999',
            sej_ticket.template_name
        ]))

    print csv_text_buffer

    archive_txt_body = "\r\n".join(archive_txt_buffer) + "\r\n"
    csv_text_body = "\r\n".join(csv_text_buffer) + "\r\n"

    zip_file_name = "/tmp/%s.zip" % template_id
    zf = EnhZipFile(zip_file_name, 'w')

    #

    zi = ZipInfo('archive.txt', time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(archive_txt_body)
    w.close()
    zf.finish_entry()

    zi = ZipInfo('TTEMPLATE.CSV', time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(csv_text_body.encode('sjis'))
    w.close()
    zf.finish_entry()

    for sej_ticket in sej_tickets:
        if sej_ticket.ticket_html:
            zi = ZipInfo("%s/%s.html" % (template_id, template_id), time.localtime()[:6])
            zi.external_attr = 0666 << 16L
            w = zf.start_entry(zi)
            w.write(sej_ticket.ticket_html)
            w.close()
            zf.finish_entry()

        if sej_ticket.ticket_css:
            zi = ZipInfo("%s/%s.css" % (template_id, template_id), time.localtime()[:6])
            zi.external_attr = 0666 << 16L
            w = zf.start_entry(zi)
            w.write(sej_ticket.ticket_css)
            w.close()
            zf.finish_entry()

    zf.close()

    # TODO SEND
    DBSession.flush()
    return zip_file_name
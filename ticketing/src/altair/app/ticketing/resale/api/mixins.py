# -*- coding: utf-8 -*-

from csv import writer as csv_writer, QUOTE_ALL
from datetime import datetime
from pyramid.response import Response


def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.replace('\r\n', '').encode('cp932')
    except UnicodeEncodeError:
        print 'cannot encode character %s to cp932' % data
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'

class CSVExportModelMixin(object):

    def _render_data(self, data):
        for record in data:
            yield map(encode_to_cp932,[
                record['id'],
                record['bank_code'],
                record['bank_branch_code'],
                record['account_type'],
                record['account_number'],
                record['account_holder_name'],
                record['total_amount']])

    def _write_file(self, file, data):
        writer = csv_writer(file, delimiter=',', quoting=QUOTE_ALL)
        writer.writerow(map(encode_to_cp932, [u"ID", u"銀行コード", u"支店コード", u"口座種別", u"口座番号", u"名義人", u"振込額"]))

        for row in self._render_data(data):
            writer.writerow(row)

    def export(self, request, *args, **kwargs):
        data = self.filter_query(self.get_query()).all()
        serializer = self.get_serializer()
        data = serializer.dump(data, many=True)
        resp = Response(status=200, headers=[
            ('Content-Type', 'text/csv'),
            ('Content-Disposition',
             'attachment; filename=resale_bank_info_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
        ])
        self._write_file(resp.body_file, data)

        return resp

class AlternativePermissionMixin(object):
    alternative_permission_classes = []

    def get_alternative_permissions(self):
        return [permission() for permission in self.alternative_permission_classes]

    def check_permission(self, request):
        super(AlternativePermissionMixin, self).check_permission(request)
        if not any([permission.has_permission(request, self) for permission in self.get_alternative_permissions()]):
            self.permission_denied(request, message=getattr(permission, 'message', None))

    def check_object_permission(self, request, obj):
        super(AlternativePermissionMixin, self).check_object_permission(request, obj)
        if not any([permission.has_object_permission(request, self, obj) for permission in self.get_alternative_permissions()]):
            self.permission_denied(request, message=getattr(permission, 'message', None))
# -*- coding: utf-8 -*-

from csv import writer as csv_writer, QUOTE_ALL
from datetime import datetime
from pyramid.response import Response

from altair.aes_urlsafe import AESURLSafe

def get_aes_crpytor():
    return AESURLSafe(key="AES_CRYPTOR_FOR_RESALE_REQUEST!!")

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


class CSVExportBaseModelMixin(object):
    def export(self, request, *args, **kwargs):
        export_type = kwargs['type']+'_' if 'type' in kwargs else None
        data = self.filter_query(self.get_query()).all()
        serializer = self.get_serializer()
        data = serializer.dump(data, many=True)
        resp = Response(status=200, headers=[
            ('Content-Type', 'text/csv'),
            ('Content-Disposition',
             'attachment; filename=resale_{export_type}info_{date}.csv'.format(
                 export_type=export_type, date=datetime.now().strftime('%Y%m%d%H%M%S')))
        ])
        self._write_file(resp.body_file, data)
        return resp


class CSVExportModelMixin(CSVExportBaseModelMixin):
    cryptor = AESURLSafe(key="AES_CRYPTOR_FOR_RESALE_REQUEST!!")

    def _render_data(self, data):
        for record in data:
            yield map(encode_to_cp932,[
                record['id'],
                record['bank_code'],
                record['bank_branch_code'],
                self.cryptor.decrypt(record['account_type'].encode('utf-8')),
                self.cryptor.decrypt(record['account_number'].encode('utf-8')),
                self.cryptor.decrypt(record['account_holder_name'].encode('utf-8')),
                record['total_amount'],
                record['order_no'],
                record['performance_name'],
                record['performance_start_on']])

    def _write_file(self, file, data):
        writer = csv_writer(file, delimiter=',', quoting=QUOTE_ALL)
        writer.writerow(map(encode_to_cp932, [u"ID", u"銀行コード", u"支店コード", u"口座種別", u"口座番号", u"名義人", u"振込額",
                                              u"受付番号", u"公演名", u"公演日時"]))

        for row in self._render_data(data):
            writer.writerow(row)

    def export(self, request, *args, **kwargs):
        return super(CSVExportModelMixin, self).export(self, request, type='bank', *args, **kwargs)


class CSVVenueExportModelMixin(CSVExportBaseModelMixin):
    def _render_data(self, data):
        for record in data:
            yield map(encode_to_cp932,[
                record['seat_name'] or u'',
                record['performance_name'] or u'',
                record['performance_start_on'] or u'',
                record['venue_name'] or u'',
                record['product_item_name'] or u''])

    def _write_file(self, file, data):
        writer = csv_writer(file, delimiter=',', quoting=QUOTE_ALL)
        writer.writerow(map(encode_to_cp932, [u"シート名", u"公演名称", u"公演日時", u"会場名", u"商品明細名"]))

        for row in self._render_data(data):
            writer.writerow(row)

    def export(self, request, *args, **kwargs):
        return super(CSVVenueExportModelMixin, self).export(self, request, type='venue', *args, **kwargs)


class CryptoMixin(object):
    cryptor = AESURLSafe(key="AES_CRYPTOR_FOR_RESALE_REQUEST!!")
    crypt_fields = []

    def _encrypt(self, data):
        if data:
            return self.cryptor.encrypt(data)
        return data

    def _decrypt(self, data):
        if data:
            return self.cryptor.decrypt(data)
        return data

    def encrypt_fields(self, data):
        for field in self.crypt_fields:
            data[field] = self._encrypt(data.get(field, u''))
        return data

    def decrypt_fields(self, data):
        for field in self.crypt_fields:
            data[field] = self._decrypt(data.get(field, u'').encode('utf-8'))
        return data

    def list(self, request, *args, **kwargs):
        data = self.filter_query(self.get_query()).all()
        serializer = self.get_serializer()
        page = self.paginate_query(data)

        if page is not None:
            data = serializer.dump(page, many=True)
            for item in data:
                self.decrypt_fields(item)

            return self.get_paginated_response(data)

        data = serializer.dump(data, many=True)
        for item in data:
            self.decrypt_fields(item)
        return Response(json=data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        instance = self.get_object()
        data = serializer.dump(instance)
        data = self.decrypt_fields(data)
        return Response(json=data)

    def perform_create(self, data):
        data = self.encrypt_fields(data)
        return super(CryptoMixin, self).perform_create(data)

    def perform_update(self, data, instance):
        data = self.encrypt_fields(data)
        return super(CryptoMixin, self).perform_update(data)


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
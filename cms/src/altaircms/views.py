# coding: utf-8
from cgi import FieldStorage
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
# from pyramid.renderers import render
# from pyramid.view import view_config

from wtforms.validators import ValidationError


class BaseRESTAPIError(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class BaseRESTAPIView(object):
    """
    フォームスキーマ、モデルを受け取り処理を実行する
    処理後はコールバックを実行する（optional）
    """

    model_object = None
    model = None
    form = None  # WTForms Form class for validate post vars.

    def __init__(self, request, id=None):
        from altaircms.models import DBSession

        self.request = request
        self.id = id

        self.session = DBSession()

    def create(self):
        (res, form) = self._validate_and_map()

        if res:
            self._create_or_update()
            url = ''
            return Response(status=201, content_location=url) # @TODO: need return new object location
        else:
            return HTTPBadRequest(form.errors)

    def read(self):
        mapper = self._get_mapper()
        content = mapper(self.model_object).as_dict()
        return Response(content, content_type='application/json', status=200)

    def update(self):
        (res, form) = self._validate_and_map()

        if res:
            self._create_or_update()
            return Response(status=200)
        else:
            return HTTPBadRequest(form.errors)

    def delete(self):
        if self.model_object:
            self.session.delete(self.model_object)
            return Response(status=200)
        else:
            return HTTPBadRequest()

    def _validate_and_map(self):
        if not self.model_object:
            self.model_object = self.model()

        form = self.form(self.request.POST)

        if not form.validate():
            return (False, form)

        for key, value in self.model_object.column_items():
            if hasattr(form, key):
                post_value = getattr(getattr(form, key), 'data')
                if isinstance(post_value, FieldStorage):
                    post_value = post_value.filename
                setattr(self.model_object, key, post_value)

        return (True, form)

    def _create_or_update(self):
        self.session.add(self.model_object)

    def _get_mapper(self):
        raise NotImplementedError()

    def get_object_by_id(self, id): #@TODO: いらなくね？
        raise NotImplementedError()

    """
    def pre_process_hook(self):
        raise NotImplementedError()

    def post_process_hook(self):
        raise NotImplementedError()
    """

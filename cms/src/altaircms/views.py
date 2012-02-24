# coding: utf-8
from cgi import FieldStorage
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
# from pyramid.renderers import render
# from pyramid.view import view_config
import transaction

from wtforms.validators import ValidationError


class BaseRESTAPIError(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class BaseRESTAPI(object):
    """
    フォームスキーマクラス、モデルクラスを受け取りCRUD処理を実行する。
    実行結果と操作対象のオブジェクトを戻り値とする。

    処理後はコールバックを実行する（optional）
    """

    model = None
    object_mapper = None
    objects_mapper = None
    form = None  # WTForms Form class for validate post vars.

    model_object = None

    def __init__(self, request, id=None):
        from altaircms.models import DBSession

        self.request = request
        self.id = id
        self.session = DBSession()
        if self.id:
            self.model_object = self.session.query(self.model).get(self.id)


    def create(self):
        """
        フォーム値を受け取ってバリデーションを行い、問題なければオブジェクトを生成する

        :return: tuple (create_status, 生成したオブジェクト, 更新エラーのdict)
        """
        (res, form) = self._validate_and_map()

        if res:
            self._create_or_update()
            return (True, self.model_object, None)
        else:
            return (False, None, form.errors)

    def read(self):
        """
        :return: object or list 指定したIDのオブジェクトまたはモデルオブジェクトのlist
        """
        if self.model_object:
            return self.model_object
        else:
            return self.session.query(self.model)

    def update(self):
        """
        :return: tuple (update_status, 更新されたオブジェクト, 更新エラーのdict)
        """
        (res, form) = self._validate_and_map()

        if res:
            self._create_or_update()
            return (True, self.model_object, None)
        else:
            return (False, None, form.errors)

    def delete(self):
        """
        :return: Boolean 削除ステータス
        """
        if self.model_object:
            self.session.delete(self.model_object)
            return True
        else:
            return False

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

    """
    def pre_process_hook(self):
        raise NotImplementedError()

    def post_process_hook(self):
        raise NotImplementedError()
    """

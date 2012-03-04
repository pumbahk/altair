# coding: utf-8
from cgi import FieldStorage
from altaircms.models import DBSession


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
    form_object = None

    def __init__(self, request, id=None):
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
        return self._create_or_update()

    def read(self):
        """
        :return: object or list 指定したIDのオブジェクトまたはモデルオブジェクトのlist
        """
        return self.model_object if self.model_object else self.session.query(self.model)

    def update(self):
        """
        :return: tuple (update_status, 更新されたオブジェクト, 更新エラーのdict)
        """
        return self._create_or_update()

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

        self.form_object = self.form(self.request.POST)
        self._post_form_hook()

        if not self.form_object.validate():
            return (False, self.form_object)

        for key, value in self.model_object.column_items():
            if hasattr(self.form_object, key):
                post_value = getattr(getattr(self.form_object, key), 'data')
                if isinstance(post_value, FieldStorage):
                    post_value = post_value.filename
                setattr(self.model_object, key, post_value)

        return (True, self.form_object)

    def _create_or_update(self):
        (res, form) = self._validate_and_map()

        if res:
            self.session.add(self.model_object)
            return (True, self.model_object, None)
        else:
            return (False, None, form.errors)

    def _post_form_hook(self):
        pass

    """
    def pre_process_hook(self):
        raise NotImplementedError()

    def post_process_hook(self):
        raise NotImplementedError()
    """

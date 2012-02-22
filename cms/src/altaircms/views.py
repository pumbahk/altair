# coding: utf-8
import deform
from deform import Form
from pyramid.httpexceptions import HTTPBadRequest
# from pyramid.renderers import render
from pyramid.response import Response
# from pyramid.view import view_config

# def render_widget(request, widget):
#     try:
#         templeate_file = 'altaircms:templates/front/widget/%s.mako' % (widget.type)
#         result = render(templeate_file, {
#                     'widget': widget
#                     },
#                     request=request
#                 )
#     except:
#         raise

#     return result

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

    validation_schema = None
    form = None
    model_object = None
    model = None

    def __init__(self, request, id=None):
        from altaircms.models import DBSession

        self.request = request
        self.id = id

        self.session = DBSession()

        self.form = Form(self.validation_schema())

    def create(self):
        try:
            self._validate_and_map()
            self._create_or_update()

            url = ''
            return Response(status=201, content_location=url) # @TODO: need return new object location
        except deform.ValidationFailure, e:
            error = e.error.asdict()
            return HTTPBadRequest(error)

    def read(self):
        mapper = self._get_mapper()
        content = mapper(self.model_object).as_dict()
        return Response(content, content_type='application/json', status=200)

    def update(self):
        try:
            self._validate_and_map()
            self._create_or_update()
            return Response(status=200)
        except deform.ValidationFailure as e:
            pass

    def delete(self):
        if self.model_object:
            self.session.delete(self.model_object)
            return Response(status=200)
        else:
            return HTTPBadRequest()

    def _validate_and_map(self):
        try:
            controls = self.request.POST.items()
            captured = self.form.validate(controls)

            if not self.model_object:
                self.model_object = self.model()

            for key, value in self.model_object.column_items():
                if key in  captured:
                    setattr(self.model_object, key, captured[key])
        except deform.ValidationFailure:
            raise

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

# -*- coding:utf-8 -*-
import wtforms
from wtforms import validators
from wtforms import fields
from wtforms import widgets


import logging
logger = logging.getLogger(__name__)
import wtforms.ext.sqlalchemy.fields as extfields
##
from wtforms.widgets.core import HTMLString
from wtforms.widgets.core import TextInput

class DatePickerInput(TextInput):
    """ a widget using bootstrap datepicker component
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            fmt = u"""
 <div class="date datepicker" data-date="">
  <input %s>
  <span class="add-on"><i class="icon-th"></i></span>
 </div>"""
            return HTMLString(fmt % self.html_params(name=field.name, **kwargs))
##
def datetime_pick_patch(): #slack-off
    """datetime field にclass="datepicker"をつける
    """ 
    target = fields.DateTimeField
    target.widget = DatePickerInput()


## custom select field
class SelectField(fields.SelectField):
    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data == self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))

class MaybeIntegerField(fields.IntegerField):
    blank_text = u"--------"
    blank_value = ""

    def __init__(self, *args, **kwargs):
        self.blank_value = kwargs.pop("blank_value", self.blank_value)
        super(MaybeIntegerField, self).__init__(*args, **kwargs)

    def process_data(self, value):
        if value is None or value == self.blank_value:
            self.data = self.blank_value
        else:
            super(MaybeIntegerField, self).process_data(value)

    def pre_validate(self, form):
        if self.data == self.blank_value:
            self.data = self.default

    def process_formdata(self, valuelist):
        if valuelist:
            v = valuelist[0] 
            if v == self.blank_value:
                self.data = None
                return 
            return super(MaybeIntegerField, self).process_formdata(valuelist)
    

from wtforms.compat import text_type
class MaybeSelectField(SelectField):
    blank_text = u"--------"
    blank_value = "_None"
    def __init__(self, label=None, validators=None, coerce=text_type, choices=None, 
                 blank_text=blank_text, blank_value=blank_value,
                 **kwargs):
        super(SelectField, self).__init__(label, validators, **kwargs)
        self.coerce = coerce
        self.choices = choices
        self.blank_text = blank_text
        self.blank_value = blank_value

    def iter_choices(self):
        yield (self.blank_value, self.blank_text, False)
        ## i'm looking forward to py3.
        for triple in super(MaybeSelectField, self).iter_choices():
            yield triple

    def process_data(self, value):
        if value is None:
            self.data = None
        elif value == self.blank_value:
            self.data = None
        else:
            super(MaybeSelectField, self).process_data(value)

    def pre_validate(self, form):
        if self.data is None or self.data == self.blank_value:
            return
        return super(MaybeSelectField, self).pre_validate(form)

    def process_formdata(self, valuelist):
        if not valuelist:
            self.data = None
        elif valuelist[0] == self.blank_value:
            self.data = None
        else:
            return super(MaybeSelectField, self).process_formdata(valuelist)

## custom multiple select field with checkbox
from wtforms.widgets import html_params
class CheckboxListWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        name = field.name
        html = [u'<div %s>' % html_params(**kwargs)]
        for val, label, status in field.iter_choices():
            if status:
                html.append(u'<span class="control-group"><label><input type="checkbox" checked="checked" name="%s" value="%s"/>%s</label></span>' % (name, val, label))
            else:
                html.append(u'<span class="control-group"><label><input type="checkbox" name="%s" value="%s"/>%s</label></span>' % (name, val, label))
        html.append(u'</div>')
        return HTMLString(''.join(html))

class CheckboxListField(fields.SelectMultipleField):
    widget = CheckboxListWidget()

##
## query_select filter
##

class myQuerySelectField(extfields.QuerySelectField):
    """ wtformsのfieldではdataのNoneの場合、常にblankが初期値として設定されてしまっていた。
    　　それへの対応
    """
    def process_data(self, value):
        if value is None:
            self.data = value
        elif hasattr(value, "__table__"):
            self.data = value
        elif isinstance(value, (int, unicode, str)):
            qs = self.query or self.query_factory()
            self.data = qs.filter_by(id=value).first() #too add-hoc
        else:
            raise ValueError("primary key or mapped object")

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, False)

        for pk, obj in self._get_object_list():
            status = self._get_selected_status(obj, self.data)
            yield (pk, self.get_label(obj), status)

    def _get_selected_status(self, obj, data):
        if data is None:
            return obj == data
        else:
            return obj.id == data.id or obj == data

class myQuerySelectMultipleField(extfields.QuerySelectMultipleField):
    def iter_choices(self):
        pks = [ x.id for x in self.data ]
        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), int(pk) in pks)

from zope.interface import Interface
from zope.interface import provider

class IModelQueryFilter(Interface):
    def __call__(model, request, query):
        """ filter by this function in before view rendering
        """
        pass

@provider(IModelQueryFilter)
def allowable_model_query(model, request, query):
    return request.allowable(model, qs=query)

def compose_dynamic_query(g, f):
    def wrapped(model, request, query):
        return g(model, request, f(model, request, query))
    return wrapped

def dynamic_query_select_field_factory(model, dynamic_query=None, name=None, break_separate=False, multiple=False, **kwargs):
    """
    dynamic_query_factory: lambda model, request, query : ...

    * query_factoryが存在していない場合は提供
    """
    if not "query_factory" in kwargs:
        def _query_factory():
            field.query = model.query
            return field.query
        kwargs["query_factory"] = _query_factory

    if multiple:
        field = myQuerySelectMultipleField(**kwargs)
    else:
        field = myQuerySelectField(**kwargs)

    name = name or model.__name__
    def dynamic_query_filter(field, form=None, rendering_val=None, request=None):
        try:
            field._object_list = None
            #hack . this is almost wrong.(if calling memoize function field.get_object_list() using this field as cache store))

            if getattr(field, "query", None):
                query = field.query
            else:
                query = field.query_factory()

            if dynamic_query:
                if not break_separate:
                    query_filter = compose_dynamic_query(dynamic_query, allowable_model_query)
                else:
                    query_filter = dynamic_query
            else:
                query_filter = allowable_model_query
            field.query = query_filter(model, request, query)
        except Exception, e:
            logger.exception(str(e))
    field._dynamic_query = dynamic_query_filter
    return field


class MaybeDateTimeField(fields.DateTimeField):
    def process_formdata(self, valuelist):
        if not valuelist:
            self.data = None
        elif valuelist[0] == u"":
            self.data = None
        else:
            super(MaybeDateTimeField, self).process_formdata(valuelist)

def required_field(message=None):
    if message is None:
        message = u"このフィールドは必須です。"
    return Required(message=message)

def append_errors(errors, key, v):
    if key not in errors:
        errors[key] = []
        errors[key].append(v)
    return errors

class Required(object):
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            if self.message is None:
                self.message = field.gettext(u'This field is required.')
            raise validators.StopValidation(self.message)

class Translations(object):
    messages={
        'Not a valid choice': u'不正な選択です',
        'Not a valid decimal value': u'数字または小数で入力してください',
        'Not a valid integer value': u'数字で入力してください',
        'Invalid email address.':u'不正なメールアドレスです',
        'This field is required.':u'入力してください',
        'Field must be at least %(min)d characters long.' : u'%(min)d文字以上で入力してください。',
        'Field cannot be longer than %(max)d characters.' : u'%(max)d文字以内で入力してください。',
        'Field must be between %(min)d and %(max)d characters long.' : u'%(min)d文字から%(max)d文字の間で入力してください。',
        'Not a valid datetime value': u'日付の形式を確認してください',
        'Invalid value for %(field)s': u'%(field)sに不正な値が入力されています',
        "Required field `%(field)s' is not supplied": u'「%(field)s」が空欄になっています',
        'year': u'年',
        'month': u'月',
        'day': u'日',
        'hour': u'時',
        'minute': u'分',
        'second': u'秒',
        }
    def __init__(self, messages = None):
        if messages:
            self.messages = dict(self.messages, **messages)

    def gettext(self, string):
        return self.messages.get(string, string)

    def ngettext(self, singular, plural, n):
        ural = singular if n == 1 else plural
        message  = self.messages.get(ural)
        if message:
            return message
        else:
            logger.warn("localize message not found: '%s'", ural)
            return ural

class Form(wtforms.Form):
    def _get_translations(self):
        return Translations()
    
class AlignChoiceField(SelectField):
    choices = (("left", u"左寄せ"), ("center", u"中央寄せ"), ("right", u"右寄せ"))
    def __init__(self, label=None, validators=None, coerce=text_type, choices=choices, 
                 **kwargs):
        super(AlignChoiceField, self).__init__(label=label, validators=validators, coerce=coerce, choices=choices, 
                 **kwargs)

    @classmethod
    def normalize_params(cls,  params):
        """this is helpers"""
        D = {}
        for k, v in params.iteritems():
            if k.startswith("data-"):
                D[k.replace("data-", "", 1)] = v
            else:
                D[k] = v
        return D

    def convert_as_style(self, align):
        if align == "left":
            return u""
        elif align == "center":
            return u'display: block; margin: 0px auto;'
        elif align == "right":
            return u"display: -webkit-box; display: -moz-box; display: -o-box; display: box; box-align: end;'"
        else:
            raise ValueError("%s is not found in candidates definition" % align)

    @classmethod
    def convert_as_html_suffix(cls, align):
        if align == "left" or align is None:
            return u""
        elif align == "right":
            return u'''<script type="text/javascript">
$(function(){
  $('img[data-align="right"]:not(.align-done)').attr("style", "float:right").addClass("clearfix").addClass("align-done");
});
</script>
'''
        elif align == "center":
            return u'''<script type="text/javascript">
$(function(){
  var ua = navigator.userAgent.toLowerCase();
  if(ua.indexOf("firefox") <= -1 && ua.indexOf("msie") <= -1){
    $('img[data-align="center"]:not(.align-done)').attr("style", "display: block; margin: 0px auto;").addClass("align-done");
  } else {
    var align_image = function align_image($e, d, retry){
      var wrapper = $e;
      for(var i=0;i<3;i++){
        wrapper = wrapper.parent();
        if(wrapper[0].nodeName != "A"){
          break;
        }
      }
      var w = $e.width();
      if(!!w && w > 0){
        $e.css("margin-left", 0.5*(wrapper.width() - w)).addClass("align-done");
      } else if(!retry){
        setTimeout(function(){align_image($e, d, true)},  d);
      }
    };
    $('img[data-align="center"]:not(.align-done)').each(function(i, e){
      var $e = $(e);
      if($e.width() <= 0){
        e.onload(function(){return align_image($e, 300, false)});
      } else {
       align_image($e, 300, false);
      }
    });
  }
});
</script>
'''
        else:
            raise ValueError("%s is not found in candidates definition" % align)
        


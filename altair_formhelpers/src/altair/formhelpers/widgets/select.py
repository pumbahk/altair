# encoding: utf-8

# https://gist.github.com/playpauseandstop/1590178

from wtforms.fields import SelectField as BaseSelectField
from wtforms.validators import ValidationError
from wtforms.widgets import HTMLString, html_params
from cgi import escape
from wtforms.widgets import Select as BaseSelectWidget
from zope.deprecation import deprecate

__all__ = [
    'GroupedSelect',
    'SelectField',
    'SelectWidget',
    ]

class GroupedSelect(BaseSelectWidget):
    def render_group(self, group_name, group):
        html = [u'<optgroup label="%s">' % group_name]
        for value, label, selected in group:
            html.append(self.render_option(value, label, selected))
        html.append(u'</optgroup>')
        return HTMLString(u''.join(html))

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for group_name, group in field.iter_choice_groups():
            if group_name is not None:
                html.append(self.render_group(group_name, group))
            else:
                for value, label, selected in group:
                    html.append(self.render_option(value, label, selected))
        html.append('</select>')
        return HTMLString(u''.join(html))


@deprecate
class SelectWidget(BaseSelectWidget):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    @classmethod
    def render_option(cls, value, label, selected):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        if isinstance(label, basestring):
            options = {'value': value}

            if selected:
                options['selected'] = u'selected'

            html = u'<option %s>%s</option>'
            data = (html_params(**options), escape(unicode(label)))
        else:
            children = []

            for item_value, item_label in label:
                item_html = cls.render_option(item_value, item_label, selected)
                children.append(item_html)

            html = u'<optgroup label="%s">%s</optgroup>'
            data = (escape(unicode(value)), u'\n'.join(children))
        return HTMLString(html % data)

@deprecate
class SelectField(BaseSelectField):
    """
    Add support of ``optgorup``'s' to default WTForms' ``SelectField`` class.

    So, next choices would be supported as well::

        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )

    """

    def pre_validate(self, form, choices=None):
        """
        Don't forget to validate also values from embedded lists.
        """
        default_choices = choices is None
        choices = choices or self.choices

        for value, label in choices:
            found = False

            if isinstance(label, (list, tuple)):
                found = self.pre_validate(form, label)

            if found or value == self.data:
                return True

        if not default_choices:
            return False

        raise ValidationError(self.gettext(u'Not a valid choice'))

# -*- coding:utf-8 -*-

""" TBA
"""

from . import helpers as h


class FormRenderer(object):

    def __init__(self, form):
        self.form = form

    def text(self, name):
        return h.text(name, value=self.form[name].data)

    def select(self, name, options):
        if self.form.errors[name]:
            pass
        else:
            return h.select(name, selected_values=self.form[name].data, options=options)

    def errors(self, name):
        return h.ul(items=self.form.errors[name])

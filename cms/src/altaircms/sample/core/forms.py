# -*- coding:utf-8 -*-

import colander
import deform

# from altaircms.page.forms import PageSchema        
class UnregisteredPageSchema(colander.MappingSchema):
    """ pageの途中のschema, layout_idとstructureは後に決める。
    """
    url = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String(), missing='')
    keyword = colander.SchemaNode(colander.String(), missing='')
    tags = colander.SchemaNode(colander.String(), missing='')

class _FormWrapper(object):
    def __init__(self, form, appstruct=None, mapper=None):
        self.form = form
        self.appstruct = mapper(appstruct) if mapper else appstruct

    def render(self):
        if self.appstruct:
            return self.form.render(self.appstruct)
        else:
            return self.form.render()

    def validate(self, appstruct):
        return self.form.validate(appstruct)

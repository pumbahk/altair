# -*- coding:utf-8 -*-

def gen(label):
    fmt =  u'<%%block name="%s">${self.inherits.%s()} ${widgets("%s")}</%%block>'
    return fmt % (label, label, label)

class TemplateGenerator(object):
    def __init__(self, super_file, keywords):
        self.super_file = super_file
        self.keywords = keywords

    def generate_inherit(self):
        return u"<%%inherit file='%s'/>" % self.super_file

    def generate_def(self):
        return u'''\
<%def name="widgets(name)">
  % for w in display_blocks[name]:
	  ${w|n}
  % endfor
</%def>
'''
    def generate(self):
        r = []
        r.append(self.generate_inherit())
        r.append(self.generate_def())
        for k in self.keywords:
            r.append(gen(k))
        return u"\n".join(r)

if __name__ == "__main__":
    tg = TemplateGenerator("altaircms:templates/front/ticket-rakuten-co-jp/layout.mako", 
                    ["header", "content", "footer"])
    print tg.generate()

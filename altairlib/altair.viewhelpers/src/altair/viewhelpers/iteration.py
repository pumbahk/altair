from .string import RawText

def first_and_last(iter, first_class=u'first', last_class=u'last'):
    first = True
    last_i = None
    extra_class = None

    def _(class_=u''):
        class_ = extra_class + u" " + class_ if extra_class else class_
        if class_:
            return RawText(u' class="%s"' % class_)
        else:
            return RawText(u'')

    for i in iter:
        if last_i is not None:
            yield _, last_i
        if first:
            extra_class = first_class
            first = False
        else:
            extra_class = None
        last_i = i

    extra_class = last_class
    if last_i is not None:
        yield _, last_i



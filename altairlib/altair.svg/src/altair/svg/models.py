# encoding: utf-8

class StyleNoneType(object):
    pass

StyleNone = StyleNoneType()

class Style(object):
    __slots__ = [
        'fill_color',
        'stroke_color',
        'stroke_width',
        'font_size',
        'font_family',
        'font_weight',
        'text_anchor',
        'line_height',
        ]

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key))

    def replace(self, **kwargs):
        params = {}
        return Style(
            **dict(
                (key, (kwargs.get(key) if kwargs.get(key) is not None else getattr(self, key)))
                for key in self.__slots__
                )
            )




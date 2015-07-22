class AnnotatedProperty(property):
    def __init__(self, *args, **kwargs):
        annotations = kwargs.pop('_annotations', None)
        for k in list(kwargs.keys()):
            if k.startswith('_a_'):
                if annotations is None:
                    annotations = {}
                annotations[k[3:]] = kwargs.pop(k)
        self._annotations = annotations
        super(AnnotatedProperty, self).__init__(*args, **kwargs)

    @property
    def __annotations__(self):
        return self._annotations

    def getter(self, f):
        return self.__class__(f, self.fset, self.fdel, _annotations=self._annotations)

    def setter(self, f):
        return self.__class__(self.fget, f, self.fdel, _annotations=self._annotations)

    def deleter(self, f):
        return self.__class__(self.fget, self.fset, f, _annotations=self._annotations)

def annotated_property(**kwargs):
    def _(f):
        return AnnotatedProperty(f, _annotations=kwargs)
    return _

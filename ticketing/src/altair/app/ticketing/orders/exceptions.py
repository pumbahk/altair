# encoding: utf-8
import traceback
from pyramid.i18n import TranslationString

class InnerCartSessionException(Exception):
    pass

class OrderCreationError(Exception):
    def __init__(self, ref, order_no, format, fargs={}, nested_exc_info=None):
        super(OrderCreationError, self).__init__(ref, order_no, format, fargs, nested_exc_info)

    @property
    def ref(self):
        return self.args[0]

    @property
    def order_no(self):
        return self.args[1]

    @property
    def format(self):
        return self.args[2]

    @property
    def fargs(self):
        return self.args[3]

    @property
    def nested_exc_info(self):
        return self.args[4]

    @property
    def message(self):
        return (TranslationString(self.format) % self.fargs).interpolate()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        buf = []
        buf.append(u'%s (%s): %s\n' % (self.ref, self.order_no, self.message))
        if self.nested_exc_info:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)

class MassOrderCreationError(Exception):
    def __init__(self, message=None, errors={}):
        super(MassOrderCreationError, self).__init__(message)
        self.errors = errors

    @property
    def message(self):
        return self.args[0]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        import six
        buf = []
        buf.append(self.message)
        if self.errors:
            for order_no, errors in six.iteritems(self.errors):
                for error in errors:
                    buf.append(unicode(error))
        return u'\n'.join(buf)

class OrderCancellationError(Exception):
    def __init__(self, order_no, format, fargs={}, nested_exc_info=None):
        super(OrderCancellationError, self).__init__(order_no, format, fargs, nested_exc_info)

    @property
    def order_no(self):
        return self.args[0]

    @property
    def format(self):
        return self.args[1]

    @property
    def fargs(self):
        return self.args[2]

    @property
    def nested_exc_info(self):
        return self.args[3]

    @property
    def message(self):
        return (TranslationString(self.format) % self.fargs).interpolate()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        buf = []
        buf.append(u'%s (%s): %s\n' % (self.ref, self.order_no, self.message))
        if self.nested_exc_info:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)

import json.encoder
from datetime import date, datetime
from altair.dynpredicate.core import Node
from altair.dynpredicate.emitters import javascript_boolean_op_func_handler, JavaScriptCodeEmitter, GenericCodeEmittingVisitor

class RawJavaScriptCode(unicode):
    pass

class JavaScriptEncoder(json.encoder.JSONEncoder):
    def _make_encoder(self, markers, encoder, floatstr, _one_shot):
        def _encoder(s):
            if isinstance(s, RawJavaScriptCode):
                return s
            else:
                return encoder(s)
        return json.encoder._make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, _one_shot)

    def iterencode(self, o, _one_shot=False):
        '''Copied from the python distribution'''
        # do nothing special if the value is scalar type
        if isinstance(o, (int, long)) or (isinstance(o, basestring) and not isinstance(o, RawJavaScriptCode)):
            return super(JavaScriptEncoder, self).iterencode(o, _one_shot)
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = json.encoder.encode_basestring_ascii
        else:
            _encoder = json.encoder.encode_basestring
        if self.encoding != 'utf-8':
            def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
                if isinstance(o, str):
                    o = o.decode(_encoding)
                return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan,
                _repr=json.encoder.FLOAT_REPR, _inf=json.encoder.INFINITY, _neginf=-json.encoder.INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text


        _iterencode = self._make_encoder(markers, _encoder, floatstr, _one_shot)
        return _iterencode(o, 0)

class DateTimeEncodingJavaScriptEncoder(JavaScriptEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return RawJavaScriptCode(
                u'new Date(%(year)s, %(month)s, %(day)s, %(hour)s, %(minute)s, %(second)s)' % dict(
                    year=self.encode(o.year),
                    month=self.encode(o.month - 1),
                    day=self.encode(o.day),
                    hour=self.encode(o.hour),
                    minute=self.encode(o.minute),
                    second=self.encode(o.second)
                    )
                )
        elif isinstance(o, date):
            return RawJavaScriptCode(
                u'new Date(%(year)s, %(month)s, %(day)s, 0, 0, 0)' % dict(
                    year=self.encode(o.year),
                    month=self.encode(o.month - 1),
                    day=self.encode(o.day)
                    )
                )
        elif isinstance(o, Node):
            emit = JavaScriptCodeEmitter()
            GenericCodeEmittingVisitor(emit, javascript_boolean_op_func_handler)(o)
            emit.buf.insert(0, u'function () { return ');
            emit.buf.append(u'; }');
            compiled_code = u''.join(emit.buf)
            return RawJavaScriptCode(compiled_code)
        else:
            return o

/* taken from Python-2.7.7/Modules/_json.c */
#include "Python.h"
#include "structmember.h"
#if PY_VERSION_HEX < 0x02060000 && !defined(Py_TYPE)
#define Py_TYPE(ob)     (((PyObject*)(ob))->ob_type)
#endif
#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#define PyInt_FromSsize_t PyInt_FromLong
#define PyInt_AsSsize_t PyInt_AsLong
#endif
#ifndef Py_IS_FINITE
#define Py_IS_FINITE(X) (!Py_IS_INFINITY(X) && !Py_IS_NAN(X))
#endif

#ifdef __GNUC__
#define UNUSED __attribute__((__unused__))
#else
#define UNUSED
#endif

#define DEFAULT_ENCODING "utf-8"

#define PyScanner_Check(op) PyObject_TypeCheck(op, &PyScannerType)
#define PyScanner_CheckExact(op) (Py_TYPE(op) == &PyScannerType)

static PyTypeObject PyScannerType;

typedef struct _PyScannerObject {
    PyObject_HEAD
    PyObject *encoding;
    PyObject *strict;
    PyObject *array_hook;
    PyObject *object_hook;
    PyObject *pairs_hook;
    PyObject *parse_float;
    PyObject *parse_int;
    PyObject *parse_constant;
} PyScannerObject;

static PyMemberDef scanner_members[] = {
    {"encoding", T_OBJECT, offsetof(PyScannerObject, encoding), READONLY, "encoding"},
    {"strict", T_OBJECT, offsetof(PyScannerObject, strict), READONLY, "strict"},
    {"array_hook", T_OBJECT, offsetof(PyScannerObject, array_hook), READONLY, "array_hook"},
    {"object_hook", T_OBJECT, offsetof(PyScannerObject, object_hook), READONLY, "object_hook"},
    {"object_pairs_hook", T_OBJECT, offsetof(PyScannerObject, pairs_hook), READONLY, "object_pairs_hook"},
    {"parse_float", T_OBJECT, offsetof(PyScannerObject, parse_float), READONLY, "parse_float"},
    {"parse_int", T_OBJECT, offsetof(PyScannerObject, parse_int), READONLY, "parse_int"},
    {"parse_constant", T_OBJECT, offsetof(PyScannerObject, parse_constant), READONLY, "parse_constant"},
    {NULL}
};

static PyObject *_str_append;

void init_json_scanner(void);
static PyObject *
scan_once_str(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr);
static PyObject *
scan_once_unicode(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr);
static PyObject *
_build_rval_index_tuple(PyObject *rval, Py_ssize_t idx);
static PyObject *
scanner_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int
scanner_init(PyObject *self, PyObject *args, PyObject *kwds);
static void
scanner_dealloc(PyObject *self);
static int
scanner_clear(PyObject *self);
static void
raise_errmsg(char *msg, PyObject *s, Py_ssize_t end);
static int
_convertPyInt_AsSsize_t(PyObject *o, Py_ssize_t *size_ptr);
static PyObject *
_convertPyInt_FromSsize_t(Py_ssize_t *size_ptr);
static int
call_append(PyObject *op, PyObject *newitem);

#define S_CHAR(c) (c >= ' ' && c <= '~' && c != '\\' && c != '"')
#define IS_WHITESPACE(c) (((c) == ' ') || ((c) == '\t') || ((c) == '\n') || ((c) == '\r'))

#define MIN_EXPANSION 6
#ifdef Py_UNICODE_WIDE
#define MAX_EXPANSION (2 * MIN_EXPANSION)
#else
#define MAX_EXPANSION MIN_EXPANSION
#endif

static int
_convertPyInt_AsSsize_t(PyObject *o, Py_ssize_t *size_ptr)
{
    /* PyObject to Py_ssize_t converter */
    *size_ptr = PyInt_AsSsize_t(o);
    if (*size_ptr == -1 && PyErr_Occurred())
        return 0;
    return 1;
}

static PyObject *
_convertPyInt_FromSsize_t(Py_ssize_t *size_ptr)
{
    /* Py_ssize_t to PyObject converter */
    return PyInt_FromSsize_t(*size_ptr);
}

static void
raise_errmsg(char *msg, PyObject *s, Py_ssize_t end)
{
    /* Use the Python function json.decoder.errmsg to raise a nice
    looking ValueError exception */
    static PyObject *errmsg_fn = NULL;
    PyObject *pymsg;
    if (errmsg_fn == NULL) {
        PyObject *decoder = PyImport_ImportModule("json.decoder");
        if (decoder == NULL)
            return;
        errmsg_fn = PyObject_GetAttrString(decoder, "errmsg");
        Py_DECREF(decoder);
        if (errmsg_fn == NULL)
            return;
    }
    pymsg = PyObject_CallFunction(errmsg_fn, "(zOO&)", msg, s, _convertPyInt_FromSsize_t, &end);
    if (pymsg) {
        PyErr_SetObject(PyExc_ValueError, pymsg);
        Py_DECREF(pymsg);
    }
}

static PyObject *
join_list_unicode(PyObject *lst)
{
    /* return u''.join(lst) */
    static PyObject *joinfn = NULL;
    if (joinfn == NULL) {
        PyObject *ustr = PyUnicode_FromUnicode(NULL, 0);
        if (ustr == NULL)
            return NULL;

        joinfn = PyObject_GetAttrString(ustr, "join");
        Py_DECREF(ustr);
        if (joinfn == NULL)
            return NULL;
    }
    return PyObject_CallFunctionObjArgs(joinfn, lst, NULL);
}

static int
call_append(PyObject *op, PyObject *newitem)
{
    PyObject *rval = PyObject_CallMethodObjArgs(op, _str_append, newitem, NULL);
    if (rval == NULL)
        return -1;
    Py_DECREF(rval);
    return 0;
}

static PyObject *
_build_rval_index_tuple(PyObject *rval, Py_ssize_t idx) {
    /* return (rval, idx) tuple, stealing reference to rval */
    PyObject *tpl;
    PyObject *pyidx;
    /*
    steal a reference to rval, returns (rval, idx)
    */
    if (rval == NULL) {
        return NULL;
    }
    pyidx = PyInt_FromSsize_t(idx);
    if (pyidx == NULL) {
        Py_DECREF(rval);
        return NULL;
    }
    tpl = PyTuple_New(2);
    if (tpl == NULL) {
        Py_DECREF(pyidx);
        Py_DECREF(rval);
        return NULL;
    }
    PyTuple_SET_ITEM(tpl, 0, rval);
    PyTuple_SET_ITEM(tpl, 1, pyidx);
    return tpl;
}

static PyObject *
scanstring_str(PyObject *pystr, Py_ssize_t end, char *encoding, int strict, Py_ssize_t *next_end_ptr)
{
    /* Read the JSON string from PyString pystr.
    end is the index of the first character after the quote.
    encoding is the encoding of pystr (must be an ASCII superset)
    if strict is zero then literal control characters are allowed
    *next_end_ptr is a return-by-reference index of the character
        after the end quote

    Return value is a new PyString (if ASCII-only) or PyUnicode
    */
    PyObject *rval;
    Py_ssize_t len = PyString_GET_SIZE(pystr);
    Py_ssize_t begin = end - 1;
    Py_ssize_t next;
    char *buf = PyString_AS_STRING(pystr);
    PyObject *chunks = PyList_New(0);
    if (chunks == NULL) {
        goto bail;
    }
    if (end < 0 || len <= end) {
        PyErr_SetString(PyExc_ValueError, "end is out of bounds");
        goto bail;
    }
    while (1) {
        /* Find the end of the string or the next escape */
        Py_UNICODE c = 0;
        PyObject *chunk = NULL;
        for (next = end; next < len; next++) {
            c = (unsigned char)buf[next];
            if (c == '"' || c == '\\') {
                break;
            }
            else if (strict && c <= 0x1f) {
                raise_errmsg("Invalid control character at", pystr, next);
                goto bail;
            }
        }
        if (!(c == '"' || c == '\\')) {
            raise_errmsg("Unterminated string starting at", pystr, begin);
            goto bail;
        }
        /* Pick up this chunk if it's not zero length */
        if (next != end) {
            PyObject *strchunk = PyString_FromStringAndSize(&buf[end], next - end);
            if (strchunk == NULL) {
                goto bail;
            }
            chunk = PyUnicode_FromEncodedObject(strchunk, encoding, NULL);
            Py_DECREF(strchunk);
            if (chunk == NULL) {
                goto bail;
            }
            if (PyList_Append(chunks, chunk)) {
                Py_DECREF(chunk);
                goto bail;
            }
            Py_DECREF(chunk);
        }
        next++;
        if (c == '"') {
            end = next;
            break;
        }
        if (next == len) {
            raise_errmsg("Unterminated string starting at", pystr, begin);
            goto bail;
        }
        c = buf[next];
        if (c != 'u') {
            /* Non-unicode backslash escapes */
            end = next + 1;
            switch (c) {
                case '"': break;
                case '\\': break;
                case '/': break;
                case 'b': c = '\b'; break;
                case 'f': c = '\f'; break;
                case 'n': c = '\n'; break;
                case 'r': c = '\r'; break;
                case 't': c = '\t'; break;
                default: c = 0;
            }
            if (c == 0) {
                raise_errmsg("Invalid \\escape", pystr, end - 2);
                goto bail;
            }
        }
        else {
            c = 0;
            next++;
            end = next + 4;
            if (end >= len) {
                raise_errmsg("Invalid \\uXXXX escape", pystr, next - 1);
                goto bail;
            }
            /* Decode 4 hex digits */
            for (; next < end; next++) {
                Py_UNICODE digit = buf[next];
                c <<= 4;
                switch (digit) {
                    case '0': case '1': case '2': case '3': case '4':
                    case '5': case '6': case '7': case '8': case '9':
                        c |= (digit - '0'); break;
                    case 'a': case 'b': case 'c': case 'd': case 'e':
                    case 'f':
                        c |= (digit - 'a' + 10); break;
                    case 'A': case 'B': case 'C': case 'D': case 'E':
                    case 'F':
                        c |= (digit - 'A' + 10); break;
                    default:
                        raise_errmsg("Invalid \\uXXXX escape", pystr, end - 5);
                        goto bail;
                }
            }
#ifdef Py_UNICODE_WIDE
            /* Surrogate pair */
            if ((c & 0xfc00) == 0xd800 && end + 6 < len &&
                buf[next++] == '\\' &&
                buf[next++] == 'u') {
                Py_UNICODE c2 = 0;
                end += 6;
                /* Decode 4 hex digits */
                for (; next < end; next++) {
                    Py_UNICODE digit = buf[next];
                    c2 <<= 4;
                    switch (digit) {
                        case '0': case '1': case '2': case '3': case '4':
                        case '5': case '6': case '7': case '8': case '9':
                            c2 |= (digit - '0'); break;
                        case 'a': case 'b': case 'c': case 'd': case 'e':
                        case 'f':
                            c2 |= (digit - 'a' + 10); break;
                        case 'A': case 'B': case 'C': case 'D': case 'E':
                        case 'F':
                            c2 |= (digit - 'A' + 10); break;
                        default:
                            raise_errmsg("Invalid \\uXXXX escape", pystr, end - 5);
                            goto bail;
                    }
                }
                if ((c2 & 0xfc00) == 0xdc00)
                    c = 0x10000 + (((c - 0xd800) << 10) | (c2 - 0xdc00));
                else
                    end -= 6;
            }
#endif
        }
        chunk = PyUnicode_FromUnicode(&c, 1);
        if (chunk == NULL) {
            goto bail;
        }
        if (PyList_Append(chunks, chunk)) {
            Py_DECREF(chunk);
            goto bail;
        }
        Py_DECREF(chunk);
    }

    rval = join_list_unicode(chunks);
    if (rval == NULL) {
        goto bail;
    }
    Py_CLEAR(chunks);
    *next_end_ptr = end;
    return rval;
bail:
    *next_end_ptr = -1;
    Py_XDECREF(chunks);
    return NULL;
}


static PyObject *
scanstring_unicode(PyObject *pystr, Py_ssize_t end, int strict, Py_ssize_t *next_end_ptr)
{
    /* Read the JSON string from PyUnicode pystr.
    end is the index of the first character after the quote.
    if strict is zero then literal control characters are allowed
    *next_end_ptr is a return-by-reference index of the character
        after the end quote

    Return value is a new PyUnicode
    */
    PyObject *rval;
    Py_ssize_t len = PyUnicode_GET_SIZE(pystr);
    Py_ssize_t begin = end - 1;
    Py_ssize_t next;
    const Py_UNICODE *buf = PyUnicode_AS_UNICODE(pystr);
    PyObject *chunks = PyList_New(0);
    if (chunks == NULL) {
        goto bail;
    }
    if (end < 0 || len <= end) {
        PyErr_SetString(PyExc_ValueError, "end is out of bounds");
        goto bail;
    }
    while (1) {
        /* Find the end of the string or the next escape */
        Py_UNICODE c = 0;
        PyObject *chunk = NULL;
        for (next = end; next < len; next++) {
            c = buf[next];
            if (c == '"' || c == '\\') {
                break;
            }
            else if (strict && c <= 0x1f) {
                raise_errmsg("Invalid control character at", pystr, next);
                goto bail;
            }
        }
        if (!(c == '"' || c == '\\')) {
            raise_errmsg("Unterminated string starting at", pystr, begin);
            goto bail;
        }
        /* Pick up this chunk if it's not zero length */
        if (next != end) {
            chunk = PyUnicode_FromUnicode(&buf[end], next - end);
            if (chunk == NULL) {
                goto bail;
            }
            if (PyList_Append(chunks, chunk)) {
                Py_DECREF(chunk);
                goto bail;
            }
            Py_DECREF(chunk);
        }
        next++;
        if (c == '"') {
            end = next;
            break;
        }
        if (next == len) {
            raise_errmsg("Unterminated string starting at", pystr, begin);
            goto bail;
        }
        c = buf[next];
        if (c != 'u') {
            /* Non-unicode backslash escapes */
            end = next + 1;
            switch (c) {
                case '"': break;
                case '\\': break;
                case '/': break;
                case 'b': c = '\b'; break;
                case 'f': c = '\f'; break;
                case 'n': c = '\n'; break;
                case 'r': c = '\r'; break;
                case 't': c = '\t'; break;
                default: c = 0;
            }
            if (c == 0) {
                raise_errmsg("Invalid \\escape", pystr, end - 2);
                goto bail;
            }
        }
        else {
            c = 0;
            next++;
            end = next + 4;
            if (end >= len) {
                raise_errmsg("Invalid \\uXXXX escape", pystr, next - 1);
                goto bail;
            }
            /* Decode 4 hex digits */
            for (; next < end; next++) {
                Py_UNICODE digit = buf[next];
                c <<= 4;
                switch (digit) {
                    case '0': case '1': case '2': case '3': case '4':
                    case '5': case '6': case '7': case '8': case '9':
                        c |= (digit - '0'); break;
                    case 'a': case 'b': case 'c': case 'd': case 'e':
                    case 'f':
                        c |= (digit - 'a' + 10); break;
                    case 'A': case 'B': case 'C': case 'D': case 'E':
                    case 'F':
                        c |= (digit - 'A' + 10); break;
                    default:
                        raise_errmsg("Invalid \\uXXXX escape", pystr, end - 5);
                        goto bail;
                }
            }
#ifdef Py_UNICODE_WIDE
            /* Surrogate pair */
            if ((c & 0xfc00) == 0xd800 && end + 6 < len &&
                buf[next++] == '\\' && buf[next++] == 'u') {
                Py_UNICODE c2 = 0;
                end += 6;
                /* Decode 4 hex digits */
                for (; next < end; next++) {
                    Py_UNICODE digit = buf[next];
                    c2 <<= 4;
                    switch (digit) {
                        case '0': case '1': case '2': case '3': case '4':
                        case '5': case '6': case '7': case '8': case '9':
                            c2 |= (digit - '0'); break;
                        case 'a': case 'b': case 'c': case 'd': case 'e':
                        case 'f':
                            c2 |= (digit - 'a' + 10); break;
                        case 'A': case 'B': case 'C': case 'D': case 'E':
                        case 'F':
                            c2 |= (digit - 'A' + 10); break;
                        default:
                            raise_errmsg("Invalid \\uXXXX escape", pystr, end - 5);
                            goto bail;
                    }
                }
                if ((c2 & 0xfc00) == 0xdc00)
                    c = 0x10000 + (((c - 0xd800) << 10) | (c2 - 0xdc00));
                else
                    end -= 6;
            }
#endif
        }
        chunk = PyUnicode_FromUnicode(&c, 1);
        if (chunk == NULL) {
            goto bail;
        }
        if (PyList_Append(chunks, chunk)) {
            Py_DECREF(chunk);
            goto bail;
        }
        Py_DECREF(chunk);
    }

    rval = join_list_unicode(chunks);
    if (rval == NULL) {
        goto bail;
    }
    Py_DECREF(chunks);
    *next_end_ptr = end;
    return rval;
bail:
    *next_end_ptr = -1;
    Py_XDECREF(chunks);
    return NULL;
}

PyDoc_STRVAR(pydoc_scanstring,
    "scanstring(basestring, end, encoding, strict=True) -> (str, end)\n"
    "\n"
    "Scan the string s for a JSON string. End is the index of the\n"
    "character in s after the quote that started the JSON string.\n"
    "Unescapes all valid JSON string escape sequences and raises ValueError\n"
    "on attempt to decode an invalid string. If strict is False then literal\n"
    "control characters are allowed in the string.\n"
    "\n"
    "Returns a tuple of the decoded string and the index of the character in s\n"
    "after the end quote."
);

static PyObject *
py_scanstring(PyObject* self UNUSED, PyObject *args)
{
    PyObject *pystr;
    PyObject *rval;
    Py_ssize_t end;
    Py_ssize_t next_end = -1;
    char *encoding = NULL;
    int strict = 1;
    if (!PyArg_ParseTuple(args, "OO&|zi:scanstring", &pystr, _convertPyInt_AsSsize_t, &end, &encoding, &strict)) {
        return NULL;
    }
    if (encoding == NULL) {
        encoding = DEFAULT_ENCODING;
    }
    if (PyString_Check(pystr)) {
        rval = scanstring_str(pystr, end, encoding, strict, &next_end);
    }
    else if (PyUnicode_Check(pystr)) {
        rval = scanstring_unicode(pystr, end, strict, &next_end);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "first argument must be a string, not %.80s",
                     Py_TYPE(pystr)->tp_name);
        return NULL;
    }
    return _build_rval_index_tuple(rval, next_end);
}

static void
scanner_dealloc(PyObject *self)
{
    /* Deallocate scanner object */
    scanner_clear(self);
    Py_TYPE(self)->tp_free(self);
}

static int
scanner_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyScannerObject *s;
    assert(PyScanner_Check(self));
    s = (PyScannerObject *)self;
    Py_VISIT(s->encoding);
    Py_VISIT(s->strict);
    Py_VISIT(s->array_hook);
    Py_VISIT(s->object_hook);
    Py_VISIT(s->pairs_hook);
    Py_VISIT(s->parse_float);
    Py_VISIT(s->parse_int);
    Py_VISIT(s->parse_constant);
    return 0;
}

static int
scanner_clear(PyObject *self)
{
    PyScannerObject *s;
    assert(PyScanner_Check(self));
    s = (PyScannerObject *)self;
    Py_CLEAR(s->encoding);
    Py_CLEAR(s->strict);
    Py_CLEAR(s->array_hook);
    Py_CLEAR(s->object_hook);
    Py_CLEAR(s->pairs_hook);
    Py_CLEAR(s->parse_float);
    Py_CLEAR(s->parse_int);
    Py_CLEAR(s->parse_constant);
    return 0;
}

static PyObject *
_parse_object_str(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON object from PyString pystr.
    idx is the index of the first character after the opening curly brace.
    *next_idx_ptr is a return-by-reference index to the first character after
        the closing curly brace.

    Returns a new PyObject (usually a dict, but object_hook can change that)
    */
    char *str = PyString_AS_STRING(pystr);
    Py_ssize_t end_idx = PyString_GET_SIZE(pystr) - 1;
    PyObject *rval;
    PyObject *pairs;
    PyObject *item;
    PyObject *key = NULL;
    PyObject *val = NULL;
    char *encoding = PyString_AS_STRING(s->encoding);
    int strict = PyObject_IsTrue(s->strict);
    Py_ssize_t next_idx;

    pairs = PyList_New(0);
    if (pairs == NULL)
        return NULL;

    /* skip whitespace after { */
    while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

    /* only loop if the object is non-empty */
    if (idx <= end_idx && str[idx] != '}') {
        while (idx <= end_idx) {
            /* read key */
            if (str[idx] != '"') {
                raise_errmsg("Expecting property name", pystr, idx);
                goto bail;
            }
            key = scanstring_str(pystr, idx + 1, encoding, strict, &next_idx);
            if (key == NULL)
                goto bail;
            idx = next_idx;

            /* skip whitespace between key and : delimiter, read :, skip whitespace */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
            if (idx > end_idx || str[idx] != ':') {
                raise_errmsg("Expecting : delimiter", pystr, idx);
                goto bail;
            }
            idx++;
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* read any JSON data type */
            val = scan_once_str(s, pystr, idx, &next_idx);
            if (val == NULL)
                goto bail;

            item = PyTuple_Pack(2, key, val);
            if (item == NULL)
                goto bail;
            Py_CLEAR(key);
            Py_CLEAR(val);
            if (PyList_Append(pairs, item) == -1) {
                Py_DECREF(item);
                goto bail;
            }
            Py_DECREF(item);
            idx = next_idx;

            /* skip whitespace before } or , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* bail if the object is closed or we didn't get the , delimiter */
            if (idx > end_idx) break;
            if (str[idx] == '}') {
                break;
            }
            else if (str[idx] != ',') {
                raise_errmsg("Expecting , delimiter", pystr, idx);
                goto bail;
            }
            idx++;

            /* skip whitespace after , delimiter */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
        }
    }
    /* verify that idx < end_idx, str[idx] should be '}' */
    if (idx > end_idx || str[idx] != '}') {
        raise_errmsg("Expecting object", pystr, end_idx);
        goto bail;
    }

    /* if pairs_hook is not None: rval = object_pairs_hook(pairs) */
    if (s->pairs_hook != Py_None) {
        val = PyObject_CallFunctionObjArgs(s->pairs_hook, pairs, NULL);
        if (val == NULL)
            goto bail;
        Py_DECREF(pairs);
        *next_idx_ptr = idx + 1;
        return val;
    }

    rval = PyObject_CallFunctionObjArgs((PyObject *)(&PyDict_Type), 
                                         pairs, NULL);
    if (rval == NULL)
        goto bail;
    Py_CLEAR(pairs);

    /* if object_hook is not None: rval = object_hook(rval) */
    if (s->object_hook != Py_None) {
        val = PyObject_CallFunctionObjArgs(s->object_hook, rval, NULL);
        if (val == NULL)
            goto bail;
        Py_DECREF(rval);
        rval = val;
        val = NULL;
    }
    *next_idx_ptr = idx + 1;
    return rval;
bail:
    Py_XDECREF(key);
    Py_XDECREF(val);
    Py_XDECREF(pairs);
    return NULL;
}

static PyObject *
_parse_object_unicode(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON object from PyUnicode pystr.
    idx is the index of the first character after the opening curly brace.
    *next_idx_ptr is a return-by-reference index to the first character after
        the closing curly brace.

    Returns a new PyObject (usually a dict, but object_hook can change that)
    */
    Py_UNICODE *str = PyUnicode_AS_UNICODE(pystr);
    Py_ssize_t end_idx = PyUnicode_GET_SIZE(pystr) - 1;
    PyObject *rval;
    PyObject *pairs;
    PyObject *item;
    PyObject *key = NULL;
    PyObject *val = NULL;
    int strict = PyObject_IsTrue(s->strict);
    Py_ssize_t next_idx;

    pairs = PyList_New(0);
    if (pairs == NULL)
        return NULL;

    /* skip whitespace after { */
    while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

    /* only loop if the object is non-empty */
    if (idx <= end_idx && str[idx] != '}') {
        while (idx <= end_idx) {
            /* read key */
            if (str[idx] != '"') {
                raise_errmsg("Expecting property name enclosed in double quotes", pystr, idx);
                goto bail;
            }
            key = scanstring_unicode(pystr, idx + 1, strict, &next_idx);
            if (key == NULL)
                goto bail;
            idx = next_idx;

            /* skip whitespace between key and : delimiter, read :, skip whitespace */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
            if (idx > end_idx || str[idx] != ':') {
                raise_errmsg("Expecting ':' delimiter", pystr, idx);
                goto bail;
            }
            idx++;
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* read any JSON term */
            val = scan_once_unicode(s, pystr, idx, &next_idx);
            if (val == NULL)
                goto bail;

            item = PyTuple_Pack(2, key, val);
            if (item == NULL)
                goto bail;
            Py_CLEAR(key);
            Py_CLEAR(val);
            if (PyList_Append(pairs, item) == -1) {
                Py_DECREF(item);
                goto bail;
            }
            Py_DECREF(item);
            idx = next_idx;

            /* skip whitespace before } or , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* bail if the object is closed or we didn't get the , delimiter */
            if (idx > end_idx) break;
            if (str[idx] == '}') {
                break;
            }
            else if (str[idx] != ',') {
                raise_errmsg("Expecting ',' delimiter", pystr, idx);
                goto bail;
            }
            idx++;

            /* skip whitespace after , delimiter */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
        }
    }

    /* verify that idx < end_idx, str[idx] should be '}' */
    if (idx > end_idx || str[idx] != '}') {
        raise_errmsg("Expecting object", pystr, end_idx);
        goto bail;
    }

    /* if pairs_hook is not None: rval = object_pairs_hook(pairs) */
    if (s->pairs_hook != Py_None) {
        val = PyObject_CallFunctionObjArgs(s->pairs_hook, pairs, NULL);
        if (val == NULL)
            goto bail;
        Py_DECREF(pairs);
        *next_idx_ptr = idx + 1;
        return val;
    }

    rval = PyObject_CallFunctionObjArgs((PyObject *)(&PyDict_Type), 
                                         pairs, NULL);
    if (rval == NULL)
        goto bail;
    Py_CLEAR(pairs);

    /* if object_hook is not None: rval = object_hook(rval) */
    if (s->object_hook != Py_None) {
        val = PyObject_CallFunctionObjArgs(s->object_hook, rval, NULL);
        if (val == NULL)
            goto bail;
        Py_DECREF(rval);
        rval = val;
        val = NULL;
    }
    *next_idx_ptr = idx + 1;
    return rval;
bail:
    Py_XDECREF(key);
    Py_XDECREF(val);
    Py_XDECREF(pairs);
    return NULL;
}

static PyObject *
_parse_array_str(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON array from PyString pystr.
    idx is the index of the first character after the opening brace.
    *next_idx_ptr is a return-by-reference index to the first character after
        the closing brace.

    Returns a new PyList
    */
    char *str = PyString_AS_STRING(pystr);
    Py_ssize_t end_idx = PyString_GET_SIZE(pystr) - 1;
    PyObject *val = NULL;
    PyObject *rval = NULL;
    Py_ssize_t next_idx;
    int (*appender)(PyObject *op, PyObject *newitem) = NULL;

    if (s->array_hook != Py_None) {
        rval = PyObject_CallFunctionObjArgs(s->array_hook, NULL);
        if (rval == NULL)
            return NULL;
        if (PyList_CheckExact(rval)) {
            appender = PyList_Append;
        } else {
            appender = call_append;
        }
    } else {
        rval = PyList_New(0);
        if (rval == NULL)
            return NULL;
        appender = PyList_Append;
    }

    /* skip whitespace after [ */
    while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

    /* only loop if the array is non-empty */
    if (idx <= end_idx && str[idx] != ']') {
        while (idx <= end_idx) {

            /* read any JSON term and de-tuplefy the (rval, idx) */
            val = scan_once_str(s, pystr, idx, &next_idx);
            if (val == NULL)
                goto bail;

            if (appender(rval, val) == -1)
                goto bail;

            Py_CLEAR(val);
            idx = next_idx;

            /* skip whitespace between term and , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* bail if the array is closed or we didn't get the , delimiter */
            if (idx > end_idx) break;
            if (str[idx] == ']') {
                break;
            }
            else if (str[idx] != ',') {
                raise_errmsg("Expecting , delimiter", pystr, idx);
                goto bail;
            }
            idx++;

            /* skip whitespace after , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
        }
    }

    /* verify that idx < end_idx, str[idx] should be ']' */
    if (idx > end_idx || str[idx] != ']') {
        raise_errmsg("Expecting object", pystr, end_idx);
        goto bail;
    }
    *next_idx_ptr = idx + 1;
    return rval;
bail:
    Py_XDECREF(val);
    Py_DECREF(rval);
    return NULL;
}

static PyObject *
_parse_array_unicode(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON array from PyString pystr.
    idx is the index of the first character after the opening brace.
    *next_idx_ptr is a return-by-reference index to the first character after
        the closing brace.

    Returns a new PyList
    */
    Py_UNICODE *str = PyUnicode_AS_UNICODE(pystr);
    Py_ssize_t end_idx = PyUnicode_GET_SIZE(pystr) - 1;
    PyObject *val = NULL;
    PyObject *rval;
    Py_ssize_t next_idx;
    int (*appender)(PyObject *op, PyObject *newitem) = NULL;

    if (s->array_hook != Py_None) {
        rval = PyObject_CallFunctionObjArgs(s->array_hook, NULL);
        if (PyList_CheckExact(rval)) {
            appender = PyList_Append;
        } else {
            appender = call_append;
        }
    } else {
        rval = PyList_New(0);
        appender = PyList_Append;
    }
    if (rval == NULL)
        return NULL;

    /* skip whitespace after [ */
    while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

    /* only loop if the array is non-empty */
    if (idx <= end_idx && str[idx] != ']') {
        while (idx <= end_idx) {

            /* read any JSON term  */
            val = scan_once_unicode(s, pystr, idx, &next_idx);
            if (val == NULL)
                goto bail;

            if (PyList_Append(rval, val) == -1)
                goto bail;

            Py_CLEAR(val);
            idx = next_idx;

            /* skip whitespace between term and , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;

            /* bail if the array is closed or we didn't get the , delimiter */
            if (idx > end_idx) break;
            if (str[idx] == ']') {
                break;
            }
            else if (str[idx] != ',') {
                raise_errmsg("Expecting ',' delimiter", pystr, idx);
                goto bail;
            }
            idx++;

            /* skip whitespace after , */
            while (idx <= end_idx && IS_WHITESPACE(str[idx])) idx++;
        }
    }

    /* verify that idx < end_idx, str[idx] should be ']' */
    if (idx > end_idx || str[idx] != ']') {
        raise_errmsg("Expecting object", pystr, end_idx);
        goto bail;
    }
    *next_idx_ptr = idx + 1;
    return rval;
bail:
    Py_XDECREF(val);
    Py_DECREF(rval);
    return NULL;
}

static PyObject *
_parse_constant(PyScannerObject *s, char *constant, Py_ssize_t idx, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON constant from PyString pystr.
    constant is the constant string that was found
        ("NaN", "Infinity", "-Infinity").
    idx is the index of the first character of the constant
    *next_idx_ptr is a return-by-reference index to the first character after
        the constant.

    Returns the result of parse_constant
    */
    PyObject *cstr;
    PyObject *rval;
    /* constant is "NaN", "Infinity", or "-Infinity" */
    cstr = PyString_InternFromString(constant);
    if (cstr == NULL)
        return NULL;

    /* rval = parse_constant(constant) */
    rval = PyObject_CallFunctionObjArgs(s->parse_constant, cstr, NULL);
    idx += PyString_GET_SIZE(cstr);
    Py_DECREF(cstr);
    *next_idx_ptr = idx;
    return rval;
}

static PyObject *
_match_number_str(PyScannerObject *s, PyObject *pystr, Py_ssize_t start, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON number from PyString pystr.
    idx is the index of the first character of the number
    *next_idx_ptr is a return-by-reference index to the first character after
        the number.

    Returns a new PyObject representation of that number:
        PyInt, PyLong, or PyFloat.
        May return other types if parse_int or parse_float are set
    */
    char *str = PyString_AS_STRING(pystr);
    Py_ssize_t end_idx = PyString_GET_SIZE(pystr) - 1;
    Py_ssize_t idx = start;
    int is_float = 0;
    PyObject *rval;
    PyObject *numstr;

    /* read a sign if it's there, make sure it's not the end of the string */
    if (str[idx] == '-') {
        idx++;
        if (idx > end_idx) {
            PyErr_SetNone(PyExc_StopIteration);
            return NULL;
        }
    }

    /* read as many integer digits as we find as long as it doesn't start with 0 */
    if (str[idx] >= '1' && str[idx] <= '9') {
        idx++;
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;
    }
    /* if it starts with 0 we only expect one integer digit */
    else if (str[idx] == '0') {
        idx++;
    }
    /* no integer digits, error */
    else {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    /* if the next char is '.' followed by a digit then read all float digits */
    if (idx < end_idx && str[idx] == '.' && str[idx + 1] >= '0' && str[idx + 1] <= '9') {
        is_float = 1;
        idx += 2;
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;
    }

    /* if the next char is 'e' or 'E' then maybe read the exponent (or backtrack) */
    if (idx < end_idx && (str[idx] == 'e' || str[idx] == 'E')) {

        /* save the index of the 'e' or 'E' just in case we need to backtrack */
        Py_ssize_t e_start = idx;
        idx++;

        /* read an exponent sign if present */
        if (idx < end_idx && (str[idx] == '-' || str[idx] == '+')) idx++;

        /* read all digits */
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;

        /* if we got a digit, then parse as float. if not, backtrack */
        if (str[idx - 1] >= '0' && str[idx - 1] <= '9') {
            is_float = 1;
        }
        else {
            idx = e_start;
        }
    }

    /* copy the section we determined to be a number */
    numstr = PyString_FromStringAndSize(&str[start], idx - start);
    if (numstr == NULL)
        return NULL;
    if (is_float) {
        /* parse as a float using a fast path if available, otherwise call user defined method */
        if (s->parse_float != (PyObject *)&PyFloat_Type) {
            rval = PyObject_CallFunctionObjArgs(s->parse_float, numstr, NULL);
        }
        else {
            double d = PyOS_string_to_double(PyString_AS_STRING(numstr),
                                             NULL, NULL);
            if (d == -1.0 && PyErr_Occurred())
                return NULL;
            rval = PyFloat_FromDouble(d);
        }
    }
    else {
        /* parse as an int using a fast path if available, otherwise call user defined method */
        if (s->parse_int != (PyObject *)&PyInt_Type) {
            rval = PyObject_CallFunctionObjArgs(s->parse_int, numstr, NULL);
        }
        else {
            rval = PyInt_FromString(PyString_AS_STRING(numstr), NULL, 10);
        }
    }
    Py_DECREF(numstr);
    *next_idx_ptr = idx;
    return rval;
}

static PyObject *
_match_number_unicode(PyScannerObject *s, PyObject *pystr, Py_ssize_t start, Py_ssize_t *next_idx_ptr) {
    /* Read a JSON number from PyUnicode pystr.
    idx is the index of the first character of the number
    *next_idx_ptr is a return-by-reference index to the first character after
        the number.

    Returns a new PyObject representation of that number:
        PyInt, PyLong, or PyFloat.
        May return other types if parse_int or parse_float are set
    */
    Py_UNICODE *str = PyUnicode_AS_UNICODE(pystr);
    Py_ssize_t end_idx = PyUnicode_GET_SIZE(pystr) - 1;
    Py_ssize_t idx = start;
    int is_float = 0;
    PyObject *rval;
    PyObject *numstr;

    /* read a sign if it's there, make sure it's not the end of the string */
    if (str[idx] == '-') {
        idx++;
        if (idx > end_idx) {
            PyErr_SetNone(PyExc_StopIteration);
            return NULL;
        }
    }

    /* read as many integer digits as we find as long as it doesn't start with 0 */
    if (str[idx] >= '1' && str[idx] <= '9') {
        idx++;
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;
    }
    /* if it starts with 0 we only expect one integer digit */
    else if (str[idx] == '0') {
        idx++;
    }
    /* no integer digits, error */
    else {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    /* if the next char is '.' followed by a digit then read all float digits */
    if (idx < end_idx && str[idx] == '.' && str[idx + 1] >= '0' && str[idx + 1] <= '9') {
        is_float = 1;
        idx += 2;
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;
    }

    /* if the next char is 'e' or 'E' then maybe read the exponent (or backtrack) */
    if (idx < end_idx && (str[idx] == 'e' || str[idx] == 'E')) {
        Py_ssize_t e_start = idx;
        idx++;

        /* read an exponent sign if present */
        if (idx < end_idx && (str[idx] == '-' || str[idx] == '+')) idx++;

        /* read all digits */
        while (idx <= end_idx && str[idx] >= '0' && str[idx] <= '9') idx++;

        /* if we got a digit, then parse as float. if not, backtrack */
        if (str[idx - 1] >= '0' && str[idx - 1] <= '9') {
            is_float = 1;
        }
        else {
            idx = e_start;
        }
    }

    /* copy the section we determined to be a number */
    numstr = PyUnicode_FromUnicode(&str[start], idx - start);
    if (numstr == NULL)
        return NULL;
    if (is_float) {
        /* parse as a float using a fast path if available, otherwise call user defined method */
        if (s->parse_float != (PyObject *)&PyFloat_Type) {
            rval = PyObject_CallFunctionObjArgs(s->parse_float, numstr, NULL);
        }
        else {
            rval = PyFloat_FromString(numstr, NULL);
        }
    }
    else {
        /* no fast path for unicode -> int, just call */
        rval = PyObject_CallFunctionObjArgs(s->parse_int, numstr, NULL);
    }
    Py_DECREF(numstr);
    *next_idx_ptr = idx;
    return rval;
}

static PyObject *
scan_once_str(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr)
{
    /* Read one JSON term (of any kind) from PyString pystr.
    idx is the index of the first character of the term
    *next_idx_ptr is a return-by-reference index to the first character after
        the number.

    Returns a new PyObject representation of the term.
    */
    PyObject *res;
    char *str = PyString_AS_STRING(pystr);
    Py_ssize_t length = PyString_GET_SIZE(pystr);
    if (idx < 0) {
        PyErr_SetString(PyExc_ValueError, "idx cannot be negative");
        return NULL;
    }
    if (idx >= length) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    switch (str[idx]) {
        case '"':
            /* string */
            return scanstring_str(pystr, idx + 1,
                PyString_AS_STRING(s->encoding),
                PyObject_IsTrue(s->strict),
                next_idx_ptr);
        case '{':
            /* object */
            if (Py_EnterRecursiveCall(" while decoding a JSON object "
                                      "from a byte string"))
                return NULL;
            res = _parse_object_str(s, pystr, idx + 1, next_idx_ptr);
            Py_LeaveRecursiveCall();
            return res;
        case '[':
            /* array */
            if (Py_EnterRecursiveCall(" while decoding a JSON array "
                                      "from a byte string"))
                return NULL;
            res = _parse_array_str(s, pystr, idx + 1, next_idx_ptr);
            Py_LeaveRecursiveCall();
            return res;
        case 'n':
            /* null */
            if ((idx + 3 < length) && str[idx + 1] == 'u' && str[idx + 2] == 'l' && str[idx + 3] == 'l') {
                Py_INCREF(Py_None);
                *next_idx_ptr = idx + 4;
                return Py_None;
            }
            break;
        case 't':
            /* true */
            if ((idx + 3 < length) && str[idx + 1] == 'r' && str[idx + 2] == 'u' && str[idx + 3] == 'e') {
                Py_INCREF(Py_True);
                *next_idx_ptr = idx + 4;
                return Py_True;
            }
            break;
        case 'f':
            /* false */
            if ((idx + 4 < length) && str[idx + 1] == 'a' && str[idx + 2] == 'l' && str[idx + 3] == 's' && str[idx + 4] == 'e') {
                Py_INCREF(Py_False);
                *next_idx_ptr = idx + 5;
                return Py_False;
            }
            break;
        case 'N':
            /* NaN */
            if ((idx + 2 < length) && str[idx + 1] == 'a' && str[idx + 2] == 'N') {
                return _parse_constant(s, "NaN", idx, next_idx_ptr);
            }
            break;
        case 'I':
            /* Infinity */
            if ((idx + 7 < length) && str[idx + 1] == 'n' && str[idx + 2] == 'f' && str[idx + 3] == 'i' && str[idx + 4] == 'n' && str[idx + 5] == 'i' && str[idx + 6] == 't' && str[idx + 7] == 'y') {
                return _parse_constant(s, "Infinity", idx, next_idx_ptr);
            }
            break;
        case '-':
            /* -Infinity */
            if ((idx + 8 < length) && str[idx + 1] == 'I' && str[idx + 2] == 'n' && str[idx + 3] == 'f' && str[idx + 4] == 'i' && str[idx + 5] == 'n' && str[idx + 6] == 'i' && str[idx + 7] == 't' && str[idx + 8] == 'y') {
                return _parse_constant(s, "-Infinity", idx, next_idx_ptr);
            }
            break;
    }
    /* Didn't find a string, object, array, or named constant. Look for a number. */
    return _match_number_str(s, pystr, idx, next_idx_ptr);
}

static PyObject *
scan_once_unicode(PyScannerObject *s, PyObject *pystr, Py_ssize_t idx, Py_ssize_t *next_idx_ptr)
{
    /* Read one JSON term (of any kind) from PyUnicode pystr.
    idx is the index of the first character of the term
    *next_idx_ptr is a return-by-reference index to the first character after
        the number.

    Returns a new PyObject representation of the term.
    */
    PyObject *res;
    Py_UNICODE *str = PyUnicode_AS_UNICODE(pystr);
    Py_ssize_t length = PyUnicode_GET_SIZE(pystr);
    if (idx < 0) {
        PyErr_SetString(PyExc_ValueError, "idx cannot be negative");
        return NULL;
    }
    if (idx >= length) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    switch (str[idx]) {
        case '"':
            /* string */
            return scanstring_unicode(pystr, idx + 1,
                PyObject_IsTrue(s->strict),
                next_idx_ptr);
        case '{':
            /* object */
            if (Py_EnterRecursiveCall(" while decoding a JSON object "
                                      "from a unicode string"))
                return NULL;
            res = _parse_object_unicode(s, pystr, idx + 1, next_idx_ptr);
            Py_LeaveRecursiveCall();
            return res;
        case '[':
            /* array */
            if (Py_EnterRecursiveCall(" while decoding a JSON array "
                                      "from a unicode string"))
                return NULL;
            res = _parse_array_unicode(s, pystr, idx + 1, next_idx_ptr);
            Py_LeaveRecursiveCall();
            return res;
        case 'n':
            /* null */
            if ((idx + 3 < length) && str[idx + 1] == 'u' && str[idx + 2] == 'l' && str[idx + 3] == 'l') {
                Py_INCREF(Py_None);
                *next_idx_ptr = idx + 4;
                return Py_None;
            }
            break;
        case 't':
            /* true */
            if ((idx + 3 < length) && str[idx + 1] == 'r' && str[idx + 2] == 'u' && str[idx + 3] == 'e') {
                Py_INCREF(Py_True);
                *next_idx_ptr = idx + 4;
                return Py_True;
            }
            break;
        case 'f':
            /* false */
            if ((idx + 4 < length) && str[idx + 1] == 'a' && str[idx + 2] == 'l' && str[idx + 3] == 's' && str[idx + 4] == 'e') {
                Py_INCREF(Py_False);
                *next_idx_ptr = idx + 5;
                return Py_False;
            }
            break;
        case 'N':
            /* NaN */
            if ((idx + 2 < length) && str[idx + 1] == 'a' && str[idx + 2] == 'N') {
                return _parse_constant(s, "NaN", idx, next_idx_ptr);
            }
            break;
        case 'I':
            /* Infinity */
            if ((idx + 7 < length) && str[idx + 1] == 'n' && str[idx + 2] == 'f' && str[idx + 3] == 'i' && str[idx + 4] == 'n' && str[idx + 5] == 'i' && str[idx + 6] == 't' && str[idx + 7] == 'y') {
                return _parse_constant(s, "Infinity", idx, next_idx_ptr);
            }
            break;
        case '-':
            /* -Infinity */
            if ((idx + 8 < length) && str[idx + 1] == 'I' && str[idx + 2] == 'n' && str[idx + 3] == 'f' && str[idx + 4] == 'i' && str[idx + 5] == 'n' && str[idx + 6] == 'i' && str[idx + 7] == 't' && str[idx + 8] == 'y') {
                return _parse_constant(s, "-Infinity", idx, next_idx_ptr);
            }
            break;
    }
    /* Didn't find a string, object, array, or named constant. Look for a number. */
    return _match_number_unicode(s, pystr, idx, next_idx_ptr);
}

static PyObject *
scanner_call(PyObject *self, PyObject *args, PyObject *kwds)
{
    /* Python callable interface to scan_once_{str,unicode} */
    PyObject *pystr;
    PyObject *rval;
    Py_ssize_t idx;
    Py_ssize_t next_idx = -1;
    static char *kwlist[] = {"string", "idx", NULL};
    PyScannerObject *s;
    assert(PyScanner_Check(self));
    s = (PyScannerObject *)self;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO&:scan_once", kwlist, &pystr, _convertPyInt_AsSsize_t, &idx))
        return NULL;

    if (PyString_Check(pystr)) {
        rval = scan_once_str(s, pystr, idx, &next_idx);
    }
    else if (PyUnicode_Check(pystr)) {
        rval = scan_once_unicode(s, pystr, idx, &next_idx);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                 "first argument must be a string, not %.80s",
                 Py_TYPE(pystr)->tp_name);
        return NULL;
    }
    return _build_rval_index_tuple(rval, next_idx);
}

static PyObject *
scanner_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyScannerObject *s;
    s = (PyScannerObject *)type->tp_alloc(type, 0);
    if (s != NULL) {
        s->encoding = NULL;
        s->strict = NULL;
        s->array_hook = NULL;
        s->object_hook = NULL;
        s->pairs_hook = NULL;
        s->parse_float = NULL;
        s->parse_int = NULL;
        s->parse_constant = NULL;
    }
    return (PyObject *)s;
}

static int
scanner_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    /* Initialize Scanner object */
    PyObject *ctx;
    static char *kwlist[] = {"context", NULL};
    PyScannerObject *s;

    assert(PyScanner_Check(self));
    s = (PyScannerObject *)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:make_scanner", kwlist, &ctx))
        return -1;

    /* PyString_AS_STRING is used on encoding */
    s->encoding = PyObject_GetAttrString(ctx, "encoding");
    if (s->encoding == NULL)
        goto bail;
    if (s->encoding == Py_None) {
        Py_DECREF(Py_None);
        s->encoding = PyString_InternFromString(DEFAULT_ENCODING);
    }
    else if (PyUnicode_Check(s->encoding)) {
        PyObject *tmp = PyUnicode_AsEncodedString(s->encoding, NULL, NULL);
        Py_DECREF(s->encoding);
        s->encoding = tmp;
    }
    if (s->encoding == NULL)
        goto bail;
    if (!PyString_Check(s->encoding)) {
	PyErr_Format(PyExc_TypeError,
		     "encoding must be a string, not %.80s",
		     Py_TYPE(s->encoding)->tp_name);
	goto bail;
    }
       

    /* All of these will fail "gracefully" so we don't need to verify them */
    s->strict = PyObject_GetAttrString(ctx, "strict");
    if (s->strict == NULL)
        goto bail;
    s->array_hook = PyObject_GetAttrString(ctx, "array_hook");
    if (s->array_hook == NULL)
        goto bail;
    s->object_hook = PyObject_GetAttrString(ctx, "object_hook");
    if (s->object_hook == NULL)
        goto bail;
    s->pairs_hook = PyObject_GetAttrString(ctx, "object_pairs_hook");
    if (s->pairs_hook == NULL)
        goto bail;
    s->parse_float = PyObject_GetAttrString(ctx, "parse_float");
    if (s->parse_float == NULL)
        goto bail;
    s->parse_int = PyObject_GetAttrString(ctx, "parse_int");
    if (s->parse_int == NULL)
        goto bail;
    s->parse_constant = PyObject_GetAttrString(ctx, "parse_constant");
    if (s->parse_constant == NULL)
        goto bail;

    return 0;

bail:
    Py_CLEAR(s->encoding);
    Py_CLEAR(s->strict);
    Py_CLEAR(s->array_hook);
    Py_CLEAR(s->object_hook);
    Py_CLEAR(s->pairs_hook);
    Py_CLEAR(s->parse_float);
    Py_CLEAR(s->parse_int);
    Py_CLEAR(s->parse_constant);
    return -1;
}

PyDoc_STRVAR(scanner_doc, "JSON scanner object");

static
PyTypeObject PyScannerType = {
    PyObject_HEAD_INIT(NULL)
    0,                    /* tp_internal */
    "_json.Scanner",       /* tp_name */
    sizeof(PyScannerObject), /* tp_basicsize */
    0,                    /* tp_itemsize */
    scanner_dealloc, /* tp_dealloc */
    0,                    /* tp_print */
    0,                    /* tp_getattr */
    0,                    /* tp_setattr */
    0,                    /* tp_compare */
    0,                    /* tp_repr */
    0,                    /* tp_as_number */
    0,                    /* tp_as_sequence */
    0,                    /* tp_as_mapping */
    0,                    /* tp_hash */
    scanner_call,         /* tp_call */
    0,                    /* tp_str */
    0,/* PyObject_GenericGetAttr, */                    /* tp_getattro */
    0,/* PyObject_GenericSetAttr, */                    /* tp_setattro */
    0,                    /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,   /* tp_flags */
    scanner_doc,          /* tp_doc */
    scanner_traverse,                    /* tp_traverse */
    scanner_clear,                    /* tp_clear */
    0,                    /* tp_richcompare */
    0,                    /* tp_weaklistoffset */
    0,                    /* tp_iter */
    0,                    /* tp_iternext */
    0,                    /* tp_methods */
    scanner_members,                    /* tp_members */
    0,                    /* tp_getset */
    0,                    /* tp_base */
    0,                    /* tp_dict */
    0,                    /* tp_descr_get */
    0,                    /* tp_descr_set */
    0,                    /* tp_dictoffset */
    scanner_init,                    /* tp_init */
    0,/* PyType_GenericAlloc, */        /* tp_alloc */
    scanner_new,          /* tp_new */
    0,/* PyObject_GC_Del, */              /* tp_free */
};

static PyMethodDef speedups_methods[] = {
    {"scanstring",
        (PyCFunction)py_scanstring,
        METH_VARARGS,
        pydoc_scanstring},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc,
"json speedups\n");

void
init_json_scanner(void)
{
    PyObject *m;
    PyScannerType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PyScannerType) < 0)
        return;
    if (!(_str_append = PyString_InternFromString("append"))) {
        return;
    }
    m = Py_InitModule3("_json_scanner", speedups_methods, module_doc);
    Py_INCREF((PyObject*)&PyScannerType);
    PyModule_AddObject(m, "make_scanner", (PyObject*)&PyScannerType);
}

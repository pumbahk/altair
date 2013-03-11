import logging
logger = logging.getLogger(__name__)
from collections import defaultdict

class Invalid(Exception):
    def __nonzero__(self):
        return False

class KeyNotFound(object):
    __slots__ = ["key", "message"]
    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __nonzero__(self):
        return False

class Result(object):
    __slots__ = ["key", "result"]
    def __init__(self, key, result):
        self.key = key
        self.result = result

class SearchSchema(object):
    def __init__(self, model, query_key, model_attribute=None, required=False):
        self.model = model
        self.query_key = query_key
        self.model_attribute = model_attribute or query_key
        self.required = required
        if not hasattr(model, self.model_attribute):
            raise Invalid("%s.%s is not found" % (model, self.model_attribute))

    def exists(self, params, query_key=None):
        query_key = query_key or self.query_key
        return query_key in params

def as_result(query_key, result):
    if isinstance(result, KeyNotFound):
        return result
    else:
        return Result(query_key, result)

class LikeSearchSchema(SearchSchema):
    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        return as_result(query_key, 
                         parse_likestring(self.model, query_key, params, self.model_attribute))

class BooleanSearchSchema(SearchSchema):
    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        return as_result(query_key, 
                         parse_boolean(self.model, query_key, params, self.model_attribute))
class ComplementSearchSchema(SearchSchema):
    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        return as_result(query_key, 
                         parse_complement(self.model, query_key, params, self.model_attribute))

class DateTimeSearchSchema(SearchSchema):
    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        return as_result(query_key, 
                         parse_datetime(self.model, query_key, params, self.model_attribute))

class DateTimeMaybeSearchSchema(SearchSchema):
    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        lhs = parse_datetime(self.model, query_key, params, self.model_attribute)
        if isinstance(lhs, KeyNotFound):
            return lhs
        return as_result(query_key, (lhs | (getattr(self.model, self.model_attribute) == None)))

class TermSearchSchema(SearchSchema):
    def __init__(self, begin, end, query_key=None):
        self.begin = begin
        self.end = end
        self.query_key = query_key

    def parse(self, params, query_key=None):
        query_key = query_key or self.query_key
        if not (self.begin.exists(params, query_key) and self.end.exists(params, query_key)):
            return KeyNotFound(query_key, "%s is not found" % query_key)
        lparams = {query_key+"_lte": params[query_key]}
        lhs = self.begin.parse(lparams, query_key=query_key)
        rparams = {query_key+"_gte": params[query_key]}
        rhs = self.end.parse(rparams, query_key=query_key)
        return as_result([lhs.key, rhs.key], lhs.result & rhs.result)

def parse_params_using_schemas(schemas, params):
    result, invalid = defaultdict(list), defaultdict(list)
    for schema in schemas:
        r = schema.parse(params)
        try:
            if isinstance(r, KeyNotFound): #xxx:
                logger.debug(r.message)
                if schema.required:
                    invalid[r.key].append(r)
            elif isinstance(r, Result):
                result[r.key].append(r.result)
            else:
                invalid(schema.query_key).append(r) ##xxx:
        except Exception, e:
            logger.debug(str(e))
            invalid[schema.query_key].append(e)
    if invalid:
        raise Invalid(invalid)
    return result


def parse_likestring(model, key, params, attr):
    if key not in params:
        return KeyNotFound(key,"%s is not found" % key)
    return getattr(model, attr).like(u"%%%s%%" % params[key])

def parse_boolean(model, key, params, attr):
    if key not in params:
        return KeyNotFound(key, "%s. operator is not found" % key)

    status = params[key]
    if status.lower() in ("true", "ok", "success", "1"):
        return getattr(model, attr) == True
    else:
        return getattr(model, attr) == False

def parse_complement(model, key, params, attr):
    if key not in params:
        return KeyNotFound(key, "%s. operator is not found" % key)

    status = params[key]
    if status.lower() in ("true", "ok", "success", "1"):
        return getattr(model, attr) == False
    else:
        return getattr(model, attr) == True

def parse_equal(model, key, params, attr):
    if key in params:
        return getattr(model, attr) == params[key]
    fkey = key + "_eq"
    if fkey in params:
        return getattr(model, attr) == params[fkey]
    fkey = key + "_neq"
    if fkey in params:
        return getattr(model, key) != params[fkey]
    return KeyNotFound(key, "%s. operator is not found" % key)

def parse_datetime(model, key, params, attr):
    fkey = key + "_lte"
    if fkey in params:
        return getattr(model, attr) <= params[fkey]
    fkey = key + "_lt"
    if fkey in params:
        return getattr(model, attr) < params[fkey]
    fkey = key + "_gte"
    if fkey in params:
        return getattr(model, attr) >= params[fkey]
    fkey = key + "_gt"
    if fkey in params:
        return getattr(model, attr) > params[fkey]
    return parse_equal(model, key, params, attr)

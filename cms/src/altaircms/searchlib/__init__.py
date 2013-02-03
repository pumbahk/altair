
class EmptyKey(object):
    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __nonzero__(self):
        return False

class SearchSchema(object):
    def __init__(self, model, query_key, model_attribute=None):
        self.model = model
        self.query_key = query_key
        self.model_attribute = model_attribute or query_key

        assert hasattr(model, self.model_attribute)

class LikeSearchSchema(SearchSchema):
    def parse(self, params):
        return parse_likestring(self.model, self.query_key, params, self.model_attribute)

class BooleanSearchSchema(SearchSchema):
    def parse(self, params):
        return parse_boolean(self.model, self.query_key, params, self.model_attribute)

class DateTimeSearchSchema(SearchSchema):
    def parse(self, params):
        return parse_datetime(self.model, self.query_key, params, self.model_attribute)

class DateTimeMaybeSearchSchema(SearchSchema):
    def parse(self, params):
        return ((parse_datetime(self.model, self.query_key, params, self.model_attribute))
                | (getattr(self.model, self.model_attribute) == None))

class TermSearchSchema(SearchSchema):
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def parse(self, params):
        return self.begin.parse(params) & self.end.parse(params)

def parse_likestring(model, key, params, attr):
    if key not in params:
        return EmptyKey(key,"%s is not found" % key)
    return getattr(model, attr).like(u"%%%s%%" % params[key])

def parse_boolean(model, key, params, attr):
    fkey = key + "_eq"
    if fkey in params:
        return getattr(model, attr) == params[fkey]
    fkey = key + "_neq"
    if fkey in params:
        return getattr(model, key) != params[fkey]
    return EmptyKey(key, "%s. operator is not found" % key)

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
    return parse_boolean(model, key, params, attr)

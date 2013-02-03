import unittest

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Article(Base):
    __tablename__ = "_article"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(30))
    publish_begin = sa.Column(sa.DateTime)
    publish_end = sa.Column(sa.DateTime)
    is_rejected = sa.Column(sa.Boolean, default=False)

class SearchQueryParseTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import LikeSearchSchema
        return LikeSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_make_one(self):
        assert Article.name
        self.assertTrue(self._makeOne(Article, "name"))

    def test_make_one_with_attribute_argument(self):
        assert Article.name
        self.assertTrue(self._makeOne(Article, "this-is-invalid-name", model_attribute="name"))

    def test_exception_occur_when_invalid_attribute(self):
        assert Article.name
        with self.assertRaises(AssertionError):
            self._makeOne(Article, "this-is-invalid-name")

    def test_exception_occur_when_invalid_attribute2(self):
        assert Article.name
        with self.assertRaises(AssertionError):
            self._makeOne(Article, "name", "this-is-invalid-name")

    def test_exists(self):
        target = self._makeOne(Article, "name")
        params = {"name": "part-of-name"}
        self.assertTrue(target.exists(params))

    def test_does_not_exists(self):
        target = self._makeOne(Article, "name")
        params = {"this-is-invalid-field": "part-of-name"}
        self.assertFalse(target.exists(params))


class AssertExpressionMixin(object):
    def assertExpression(self, result, expected):
        # slack-off
        self.assertEqual(str(result), str(expected))

class BooleanSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import BooleanSearchSchema
        return BooleanSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne(Article, "is_rejected")
        params = {"is_rejected": "True"}

        result = target.parse(params)
        self.assertExpression(result.result, Article.is_rejected == True)

    def test_false(self):
        target = self._makeOne(Article, "is_rejected")
        params = {"is_rejected": "False"}

        result = target.parse(params)
        self.assertExpression(result.result, Article.is_rejected == False)

    def test_query_key_is_not_found_then_return_none(self):
        target = self._makeOne(Article, "is_rejected")
        params = {}

        result = target.parse(params)
        self.assertFalse(result)
        self.assertEqual(result.key, "is_rejected")

class LikeSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import LikeSearchSchema
        return LikeSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne(Article, "name")
        params = {"name": "part-of-name"}

        result = target.parse(params)
        self.assertExpression(result.result, Article.name.like("%part-of-name%"))

    def test_query_key_is_not_found_then_return_none(self):
        target = self._makeOne(Article, "name")
        params = {}

        result = target.parse(params)
        self.assertFalse(result)
        self.assertEqual(result.key, "name")

class DateTimeSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import DateTimeSearchSchema
        return DateTimeSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_query_key_is_not_found_then_return_none(self):
        target = self._makeOne(Article, "publish_begin")
        params = {}

        result = target.parse(params)
        self.assertFalse(result)
        self.assertEqual(result.key, "publish_begin")

    def test_parse_eq(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_eq": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin == params["publish_begin_eq"])

    def test_parse_neq(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_neq": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin != params["publish_begin_neq"])

    def test_parse_lte(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_lte": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin <= params["publish_begin_lte"])

    def test_parse_lt(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_lt": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin < params["publish_begin_lt"])

    def test_parse_gte(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_gte": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin >= params["publish_begin_gte"])

    def test_parse_gt(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_begin")
        params = {"publish_begin_gt": datetime(1900, 1, 1)}

        result = target.parse(params)
        self.assertExpression(result.result, Article.publish_begin > params["publish_begin_gt"])

class DateTimeMaybeSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import DateTimeMaybeSearchSchema
        return DateTimeMaybeSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_maybe(self):
        from datetime import datetime
        target = self._makeOne(Article, "publish_end")
        params = {"publish_end_gt": datetime(1900, 1, 1)}

        result = target.parse(params)
        expected = ((Article.publish_end > params["publish_end_gt"]) | 
                    (Article.publish_end == None))
        
        self.assertExpression(result.result, expected)

class TermSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _getTarget(self):
        from altaircms.searchlib import TermSearchSchema
        return TermSearchSchema

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_maybe(self):
        from altaircms.searchlib import DateTimeSearchSchema
        from altaircms.searchlib import DateTimeMaybeSearchSchema

        from datetime import datetime
        target = self._makeOne(DateTimeSearchSchema(Article, "publish_begin"), 
                               DateTimeMaybeSearchSchema(Article, "publish_end"), 
                               query_key="in_term")
        params = {"in_term": datetime(1900, 1, 1)}

        result = target.parse(params)
        lhs = Article.publish_begin <= params["in_term"]
        rhs = ((Article.publish_end >= params["in_term"]) | 
               (Article.publish_end == None))
        expected = lhs & rhs
        self.assertExpression(result.result, expected)

class CompoundSearchQueryParseTests(AssertExpressionMixin, unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.searchlib import parse_params_using_schemas
        return parse_params_using_schemas(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        from altaircms.searchlib import LikeSearchSchema
        from altaircms.searchlib import DateTimeSearchSchema
        from altaircms.searchlib import DateTimeMaybeSearchSchema
        schemas = [LikeSearchSchema(Article, "name"), 
                   DateTimeSearchSchema(Article, "term_begin", "publish_begin"), 
                   DateTimeMaybeSearchSchema(Article, "term_end", "publish_end"), 
                   ]
        params = {"name": "part-of-article", 
                  "term_begin_gte": datetime(1900, 1, 1), 
                  "term_end_lte": datetime(3000, 1, 1)}

        result = self._callFUT(schemas, params)
        self.assertExpression(result["name"][0], Article.name.like("%%part-of-article%%"))
        self.assertExpression(result["term_begin"][0], Article.publish_begin >= datetime(1900, 1, 1))
        self.assertExpression(result["term_end"][0], (Article.publish_end <= datetime(3000, 1, 1)) | (Article.publish_end == None))

    def test_does_not_exist(self):
        from altaircms.searchlib import LikeSearchSchema
        from altaircms.searchlib import DateTimeSearchSchema
        from altaircms.searchlib import DateTimeMaybeSearchSchema
        schemas = [LikeSearchSchema(Article, "name"), 
                   DateTimeSearchSchema(Article, "term_begin", "publish_begin"), 
                   DateTimeMaybeSearchSchema(Article, "term_end", "publish_end"), 
                   ]
        params = {"name": "part-of-article"}

        result = self._callFUT(schemas, params)
        self.assertExpression(result["name"][0], Article.name.like("%%part-of-article%%"))

if __name__ == "__main__":
    unittest.main()

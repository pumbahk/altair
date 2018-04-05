# -*- coding: utf-8 -*-

from sqlalchemy import or_, func, Unicode, cast

class BaseFilter(object):
    """Base filter class that all filter classes must inherit"""

    def filter_query(self, request, query, view):
        raise NotImplementedError('`filter_query` must be implemented.')

class AttributeBaseFilter(BaseFilter):
    """
    A base class for implementing filters on SQLAlchemy model attributes.
    Supports filtering a comma separated list using OR statements and relationship filter using
    the . path to attribute.

    Expects the query string  parameters to be formatted as : `key[field_name]=val`.
    """

    # The key to use when parsing the request's query string. The key in `key[field_name] = val`
    query_string_lookup = None

    # The name of the class attribute used in the view class that uses the filter the specifies
    # which filed can be filtered on.
    view_attribute_name = None

    def parse_query_string(self, params):

        results = {}

        for key, val in params.items():
            lookup_len = len(self.query_string_lookup) + 1

            if key[0:lookup_len] == '{}['.format(self.query_string_lookup) and key[-1] == ']':
                results[key[lookup_len:-1]] = val if val.lower() != 'null' else None

        return results

    def filter_query(self, request, query, view):
        if not request.params:
            return query

        querystring_params = self.parse_query_string(request.params)
        query, filter_list = self.build_filter_list(querystring_params, query, view)

        return self.apply_filter(query, filter_list)

    def get_filterable_field(self, filterable_field_string, model):
        model_name, attr_name = filterable_field_string.split('.')
        if model.__name__ == model_name and hasattr(model, attr_name):
            return getattr(model, attr_name)


    def build_filter_list(self, querystring_params, query, view):
        filterable_fields = getattr(view, self.view_attribute_name, None)
        if not filterable_fields:
            return query, []

        filter_list = []

        for key, val in querystring_params.items():
            attrs = key.split('.')
            related_model = view.model
            join_models = []

            for attr in attrs[:-1]:

                relationship = getattr(related_model, attr, None)

                if relationship is None:
                    related_model = None
                    break

                related_model = relationship.mapper.class_
                join_models.append(related_model)

            attr = attrs[-1]

            if related_model and hasattr(related_model, attr):
                try:
                    i = filterable_fields.index('{}.{}'.format(related_model.__name__, attr))
                except ValueError:
                    continue

                joined_tables = [mapper.class_ for mapper in query._join_entities]

                for join_model in join_models:
                    if join_model not in joined_tables:
                        query = query.join(join_model)

                filter_list.append(self.build_comparision(self.get_filterable_field(filterable_fields[i], related_model), val))

        return query, filter_list

    def apply_filter(self, query, filter_list):

        return query.filter(*filter_list)

    def build_comparision(self, field, value):
        raise NotImplementedError

class FieldFilter(AttributeBaseFilter):

    query_string_lookup = 'filter'
    view_attribute_name = 'filter_fields'

    def build_comparision(self, field, value):
        if value is None:
            return field == None

        return or_(*[field == v for v in value.split(',')])

class SearchFilter(AttributeBaseFilter):

    query_string_lookup = 'search'
    view_attribute_name = 'search_fields'

    def build_comparision(self, field, value):
        if value is None:
            return field == None

        return or_(*[func.lower(cast(field, Unicode)).like(u'%{}%'.format(v.lower())) for v in value.split(',')])

    def apply_filter(self, query, filter_list):

        return query.filter(or_(*filter_list))

class OrderFilter(AttributeBaseFilter):

    query_string_lookup = 'order'
    view_attribute_name = 'order_fields'

    def build_comparision(self, field, value):
        return field if value != 'desc' else field.desc()

    def apply_filter(self, query, filter_list):
        return query.order_by(*filter_list)
import json
import sqlahelper
import sys
import sqlalchemy as sa
import altaircms.event.models
import functools
import altaircms.page.models
import tableau as t
from altaircms.models import Genre
from altaircms.scripts.misc.dataset import DataSuite, WithCallbackDataSet
from tableau.sqla import newSADatum
from tableau import DataWalker
from tableau.sql import SQLGenerator

# def parse(params, ancestors, result):
#     target = Genre(name=params["name"], label=params["label"])
#     result.append(target)
#     if "children" in params:
#         ancestors.insert(0, target)
#         for sub_params in params["children"]:
#             child = parse(sub_params, ancestors, result)
#             for i, p in enumerate(ancestors):
#                 child._add_parent(p, hop=i+1)
#     return target

class FixtureBuilder(object):
    def __init__(self, Datum):
        class _Datum(Datum):
            def __init__(self, schema, **fields):
                Datum.__init__(self, schema, t.auto("id"), **fields)
        self.Datum = _Datum
        self._Datum = Datum

    def parse(self, params, ancestors, result):
        target = self.Datum("Genre", name=params["name"], label=params["label"])
        result.append(target)
        if "children" in params:
            ancestors.insert(0, target)
            for sub_params in params["children"]:
                child = self.parse(sub_params, ancestors, result)
                for i, p in enumerate(ancestors):
                    # child._add_parent(p, hop=i+1)
                    self.result.append(self.Datum("genre_path"), genre=child, next_genre=p, hop=i+1)
        return target

    def build(self, params):
        result = []
        ancestors = []
        self.parse(params, ancestors, result)
        return self.result

class WithOffset(object):
    """ insert sql id with offset value

    e.g. offset = 10
    insert statment start from id=11
    """
    def __init__(self):
        self.offset_table = {}
        self.session = sqlahelper.get_session()
        self.table_to_declarative = self.collect_declarative(sqlahelper.get_base())

    def collect_declarative(self, base):
        table_to_declarative = {}
        if base is not None:
            for class_name, declarative in base._decl_class_registry.items():
                table_to_declarative[declarative.__table__.name] = declarative
        return table_to_declarative

    def _get_offset_value(self, schema, data):
        cls = self.table_to_declarative[schema]
        return cls.query.with_entities(sa.func.Max(cls.id)).scalar() or 0

    def get_offset_value(self, schema, data): #memoize function
        if not schema in self.offset_table:
            self.offset_table[schema] = self._get_offset_value(schema, data)
        return self.offset_table[schema]
        
    def setvalue(self, data, datum):
        schema = datum._tableau_table.name
        offset = self.get_offset_value(schema, datum)
        pk = data.seq + offset
        setattr(datum, datum._tableau_id_fields[0], pk)
        assert getattr(datum, datum._tableau_id_fields[0], pk)


def main(args):
    engine = args[1]
    jsonfile = args[2]
    sqlahelper.add_engine(sa.create_engine(engine))

    Base = sqlahelper.get_base()
    Datum = newSADatum(Base.metadata)

    builder =FixtureBuilder(Datum)
    suite = DataSuite(dataset_impl=functools.partial(WithCallbackDataSet, on_autoid=WithOffset()))
    walker = DataWalker(suite)

    with open(jsonfile,"r") as rf:
        for datum in builder.build(json.load(rf, encoding="utf-8")):
            walker(datum)
    SQLGenerator(sys.stdout, encoding='utf-8')(suite)

main(sys.argv)


    

import logging
from tableau.dataset import DataSuite as OriginalDataSuite
from tableau.dataset import DataSet
from tableau.declarations import auto

## todo: patch

class DefaultAutoIdDetect(object):
    @staticmethod
    def setvalue(dataset, datum):
        setattr(datum, datum._tableau_id_fields[0], dataset.seq)
        assert getattr(datum, datum._tableau_id_fields[0], dataset.seq)


import sqlahelper
import sqlalchemy as sa

class WithOffset(object):
    """ insert sql id with offset value

    e.g. offset = 10
    insert statment start from id=11
    """
    def __init__(self, session):
        self.session = session
        self.offset_table = {}
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
        
    def setvalue(self, dataset, datum):
        schema = datum._tableau_table.name
        offset = self.get_offset_value(schema, datum)
        pk = dataset.seq + offset
        setattr(datum, datum._tableau_id_fields[0], pk)
        assert getattr(datum, datum._tableau_id_fields[0], pk)
#

class WithCallbackDataSet(DataSet):
    def __init__(self, schema, on_autoid=DefaultAutoIdDetect(), **kwargs):
        super(WithCallbackDataSet, self).__init__(schema, **kwargs)
        self.on_autoid = on_autoid

    def add(self, datum):
        if datum in self.data:
            return False

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Trying to add %s' % datum)

        if isinstance(datum._tableau_id_fields, auto):
            self.on_autoid.setvalue(self, datum)
            self.seq += 1
        self.data.add(datum)
        return True

class DataSuite(OriginalDataSuite):
    def __init__(self, dataset_impl=WithCallbackDataSet):
        super(DataSuite, self).__init__()
        self.DataSet = dataset_impl

    def __getitem__(self, schema):
        dataset = self.datasets.get(schema)
        if dataset is None:
            self.digraph.add_reference(schema, None)
            dataset = self.DataSet(schema)
            self.datasets[schema] = dataset
        return dataset

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


class WithCallbackDataSet(DataSet):
    def __init__(self, schema, on_autoid=DefaultAutoIdDetect, **kwargs):
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

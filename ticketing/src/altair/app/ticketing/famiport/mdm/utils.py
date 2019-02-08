import csv
import six

from codecs import getencoder
from altair.app.ticketing.famiport.datainterchange.fileio import CSVRecordMarshaller, RecordUnmarshaller


def make_marshaller(f, schema, encoding='CP932'):
    """
    Generates marshaller object.
    :param f: file object
    :param schema: list consisting of schemas defining columns
    :param encoding: encoding to write lines of csv file with
    :return: marshaller object
    """
    encoder = getencoder(encoding)
    marshaller = CSVRecordMarshaller(schema)

    def out(rendered):
        f.write(encoder(rendered)[0])

    def _(row):
        return marshaller(row, out)

    return _


def make_unmarshaller(f, schema, encoding='CP932', exc_handler=None):
    """
    Generates unmarshaller object.
    :param f: file object
    :param schema:list consisting of schemas defining columns
    :param encoding: encoding to read lines of csv file with
    :param exc_handler: handler function called when any exception occurs
    :return: unmarshaller object
    """
    def _(f2):
        for r in csv.reader(f2):
            yield [six.text_type(c, encoding) for c in r]
    return RecordUnmarshaller(schema, exc_handler=exc_handler)(_(f))

import sys

"""
todo: output meessage via logger
"""

def _create_db(Base, DBSession, engine):
    if not Base.metadata.is_bound():
        Base.metadata.bind = engine
    if not DBSession.bind and not DBSession.registry.has():
        DBSession.configure(bind=engine)
    Base.metadata.create_all()
    # listing_all(Base.metadata)
    return DBSession

def _message(message):
    if message:
        sys.stderr.write("----------------\n")
        sys.stderr.write(message)
        sys.stderr.write("\n----------------\n")

def create_db(echo=False, base=None, session=None, message=None):
    # _message(message)

    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///')
    engine.echo = echo
    if base is None or session is None:
        import altaircms.models as m
        return _create_db(m.Base, m.DBSession, engine)
    else:
        return _create_db(base, session, engine)


def dropall_db(base=None, session=None, message=None):
    if base is None or session is None:
        import altaircms.models as m
        # listing_all(m.Base.metadata)
        m.Base.metadata.drop_all(bind=m.DBSession.bind)
    else:
        # listing_all(base.metadata)
        base.metadata.drop_all(bind=session.bind)




from sqlalchemy.engine.ddl import DDLBase
from sqlalchemy import schema
from sqlalchemy.sql import util as sql_util

class SchemaListing(DDLBase):
    def __init__(self, dialect, connection, checkfirst=False, tables=None, **kwargs):
        super(SchemaListing, self).__init__(connection, **kwargs)
        self.checkfirst = checkfirst
        self.tables = tables and set(tables) or None
        self.preparer = dialect.identifier_preparer
        self.dialect = dialect
        self.memo = {}

    def visit_metadata(self, metadata):
        if self.tables:
            tables = self.tables
        else:
            tables = metadata.tables.values()
        collection = [t for t in sql_util.sort_tables(tables)]
        # seq_coll = [s for s in metadata._sequences.values()]
        # for seq in seq_coll:
        #     self.traverse_single(seq, listing_need=True)

        for table in collection:
            self.traverse_single(table, listing_need=True)

    def _can_listing_table(self, table):
        self.dialect.validate_identifier(table.name)
        if table.schema:
            self.dialect.validate_identifier(table.schema)
        return not self.checkfirst or self.dialect.has_table(self.connection, 
                                            table.name, schema=table.schema)

    def visit_table(self, table, listing_need=False):
        if not listing_need and not self._can_listing_table(table):
            return

        # for column in table.columns:
        #     if column.default is not None:
        #         self.traverse_single(column.default)

        print "table: %s" % table
        result = self.connection.execute(schema.DDL("SELECT * FROM %s;" % table))
        for row in result:
            print "\t%s" % row

        # if hasattr(table, 'indexes'):
        #     for index in table.indexes:
        #         self.traverse_single(index)

    def visit_sequence(self, sequence, listing_need=False):
        pass
        # self.connection.execute(schema.CreateSequence(sequence))

    def visit_index(self, index):
        pass

def listing_all(metadata, bind=None, tables=None, checkfirst=True):
    if bind is None:
        bind = metadata.bind
    bind._run_visitor(SchemaListing, 
                      metadata, 
                      checkfirst=checkfirst,
                      tables=tables)


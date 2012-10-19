from tableau.sql import SQLBuilder, InsertStmtBuilder
import sys
builder = SQLBuilder(sys.stdout, encoding="utf8")
builder.insert("foo", [1, 2, 3])

import sys
import json
from collections import namedtuple 
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
Genre = namedtuple("genre", "id name label organization_id")
GenrePath = namedtuple("genre_path", "genre_id next_id hop")

class Counter(object):
    def __init__(self, i=0):
        self.i = i

    def inc(self):
        self.i += 1
        return self.i

class SQLObject(object):
    def __init__(self, out=sys.stdout):
        self.out = out

    def insert(self, o):
        name = o.__class__.__name__
        fields = " ".join(o._fields)
        values = u" ".join('"%s"' % v if isinstance(v, (str, unicode)) else str(v) for v in list(o))
        self.out.write(u'INSERT INTO %s (%s) VALUES (%s)\n' % (name, fields, values))
        

organization_id = 1
Genre_id = Counter(0)

def parse(params, ancestors, result):
    target = Genre(id=Genre_id.inc(), name=params["name"], label=params["label"], organization_id=organization_id)
    result.append(target)
    if "children" in params:
        ancestors.insert(0, target)
        for sub_params in params["children"]:
            child = parse(sub_params, ancestors, result)
            for i, p in enumerate(ancestors):
                path = GenrePath(genre_id=child.id, next_id=target.id, hop=i+1)
                result.append(path)
        ancestors.pop(0)
    return target


def main(args):
    with open(args[1],"r") as rf:
        result = []
        ancestors = []
        sql = SQLObject()
        parse(json.load(rf, encoding="utf-8"), ancestors, result)
        for o in result:
            sql.insert(o)

main(sys.argv)
    

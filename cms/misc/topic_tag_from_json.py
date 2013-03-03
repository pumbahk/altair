import json
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
from collections import namedtuple 

TopicTag = namedtuple("topiccoretag", "label publicp type")

class SQLObject(object):
    def __init__(self, out=sys.stdout):
        self.out = out

    def insert(self, o):
        name = o.__class__.__name__
        fields = ", ".join(o._fields)
        values = u",".join('"%s"' % v if isinstance(v, (str, unicode)) else str(v) for v in list(o))
        self.out.write(u'INSERT INTO %s (%s) VALUES (%s);\n' % (name, fields, values))


def create_tags(target):
    return [
        TopicTag(label=target["label"], publicp=True, type="topic"), 
        TopicTag(label=target["label"], publicp=True, type="topcontent"), 
        TopicTag(label=target["label"], publicp=True, type="promotion"), 
        ]

def parse(params, result):
    for tag in create_tags(params):
        result.append(tag)
    if "children" in params:
        for sub_params in params["children"]:
            parse(sub_params, result)
    return result

def main(args):
    with open(args[1],"r") as rf:
        result = []
        sql = SQLObject()
        parse(json.load(rf, encoding="utf-8"), result)
        for o in result:
            sql.insert(o)

main(sys.argv)

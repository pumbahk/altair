import sys
from StringIO import StringIO
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

from ticketing.tickets.cleaner.api import get_validated_svg_cleaner


def normalized_xml(svg_string):
    io = StringIO(svg_string.encode("utf-8"))
    cleaner = get_validated_svg_cleaner(io)
    return cleaner.get_cleaned_svgio().getvalue()

server = SimpleJSONRPCServer(('localhost', 4445))
server.register_function(lambda x: x+1, 'inc')
server.register_function(normalized_xml, "normalized_xml")

sys.stderr.write("port: %s\n" % "localhost:4445")
server.serve_forever()

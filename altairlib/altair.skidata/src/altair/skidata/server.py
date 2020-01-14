import SimpleHTTPServer
import SocketServer
import httplib
import logging
import re
import socket
from threading import Thread

from altair.skidata.exceptions import SkidataUnmarshalFailed
from altair.skidata.marshaller import SkidataXmlMarshaller
from altair.skidata.models import TSData, HSHData, Error, HSHErrorType, HSHErrorNumber, \
    Envelope, Body, ProcessRequestResponse, ProcessRequest, Header
from altair.skidata.unmarshaller import SkidataXmlUnmarshaller

logger = logging.getLogger(__name__)


def start_local_hsh_server():
    port = get_free_port()
    server = HSHServer(port)
    server.start()
    return 'http://localhost:{port}/ImporterWebService'.format(port=port)


def get_free_port():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    # bind an available port
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


DEFAULT_ENCODING = 'utf-8'


class TSRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        """Serve as a Post request.
        Parse Skidata XML request data and accept as a success data simply when
        the data contains TSData Element with Header Element.

        status codes
        200: Request XML contains TSData Element with Header Element.
        400: Request data is empty
        415: Content-Type is not text/xml;charset=utf-8
        500: Illegal XML data
        """
        content_type = self.headers.get('Content-Type', '').lower()
        if re.match(r'^\s*text/xml\s*;\s*charset=\s*utf-8\s*(;.*)?$', content_type) is None:
            self.send_error(httplib.UNSUPPORTED_MEDIA_TYPE)
            return

        data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        if not data:
            self.send_error(httplib.BAD_REQUEST)
            return

        try:
            envelope = self._parse_data(data)
            xml = SkidataXmlMarshaller.marshal(envelope, encoding=DEFAULT_ENCODING, pretty_print=True)

            self.send_response(httplib.OK)
            self.send_header('Content-type', 'text/xml; charset={}'.format(DEFAULT_ENCODING))
            self.end_headers()

            self.wfile.write(xml)
        except SkidataUnmarshalFailed as e:
            self.send_error(httplib.INTERNAL_SERVER_ERROR, e.message)
        except Exception as e:
            self.send_error(httplib.INTERNAL_SERVER_ERROR, str(e))

    def _parse_data(self, data):
        envelope = SkidataXmlUnmarshaller.unmarshal(data, Envelope)

        body = envelope.body()
        if not isinstance(body, Body):
            return self._make_envelope_with_error()

        process_request = body.process_request()
        if not isinstance(process_request, ProcessRequest):
            return self._make_envelope_with_error()

        ts_data = process_request.ts_data()
        if not isinstance(ts_data, TSData):
            return self._make_envelope_with_error()

        header = ts_data.header()
        if not isinstance(header, Header):
            return self._make_envelope_with_error()

        return self._make_envelope(header)

    def _make_envelope_with_error(self):
        """Make Envelope with Error in which the fix values are set"""
        error = Error(type_=HSHErrorType.STOP,
                      number=HSHErrorNumber.HSH_INTERNAL_ERROR,
                      description='HSH internal error')

        header = Header(version='HSHIF25', issuer='1')
        return self._make_envelope(header=header, error=error)

    @staticmethod
    def _make_envelope(header, error=None):
        hsh_data = HSHData(header=header, error=error)

        marshaled_hsh_data = SkidataXmlMarshaller.marshal(hsh_data, encoding=DEFAULT_ENCODING)
        process_response = ProcessRequestResponse(hsh_data=marshaled_hsh_data.decode(DEFAULT_ENCODING))

        body = Body(process_response=process_response)
        return Envelope(body=body)


class HSHServer(object):
    def __init__(self, port):
        self._server = SocketServer.TCPServer(('localhost', port), TSRequestHandler)

    def start(self):
        """Start running a local server in a separate thread."""
        thread = Thread(target=self._server.serve_forever)
        thread.setDaemon(True)
        thread.start()

class CommunicationError(Exception):
    def __init__(self, message, status=None):
        super(CommunicationError, self).__init__(message, status)

    @property
    def message(self):
        return self.args[0]

    @property
    def status(self):
        return self.args[1]


class InvalidPayloadError(CommunicationError):
    pass


class GenericHTTPError(CommunicationError):
    pass


class GenericError(CommunicationError):
    pass

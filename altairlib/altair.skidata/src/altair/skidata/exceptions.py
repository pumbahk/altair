class SkidataWebServiceError(Exception):
    """Web Service error"""
    @property
    def code(self):
        return 'SKI0001'

    def __str__(self):
        return u'[{code}] {msg}'.format(code=self.code, msg=self.message)


class SkidataMarshalFailed(Exception):
    """Marshalling error when serializing Skidata Model to an XML data"""
    @property
    def code(self):
        return 'SKI0002'

    def __str__(self):
        return u'[{code}] {msg}'.format(code=self.code, msg=self.message)


class SkidataUnmarshalFailed(Exception):
    """Unmarshalling error when deserializing an XML data to Skidata Model"""
    @property
    def code(self):
        return 'SKI0003'

    def __str__(self):
        return u'[{code}] {msg}'.format(code=self.code, msg=self.message)

class SkidataWebServiceError(Exception):
    """Web Service error"""


class SkidataMarshalFailed(Exception):
    """Marshalling error when serializing Skidata Model to an XML data"""


class SkidataUnmarshalFailed(Exception):
    """Unmarshalling error when deserializing an XML data to Skidata Model"""

# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from xml.etree import ElementTree
from xml.dom import minidom

class FamiPortCrypt:
    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt(self, plain_data):
        """
        Encrypt plain_data with the given key in init
        :param plain_data:
        :return: encrypted data
        """

        return self.fernet.encrypt(plain_data)

    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted_data with the given key in init
        :param encrypted data:
        :return: decrypted data
        """

        return self.fernet.decrypt(encrypted_data)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

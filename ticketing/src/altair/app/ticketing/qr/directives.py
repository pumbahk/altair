# -*- coding:utf-8 -*-
import logging
from .interfaces import IQRAESPlugin, IQRAESDeliveryFormMaker

logger = logging.getLogger(__name__)

QE_AES_CONFIG = -10

class Discriminator(object):
    __slot__ = (
        'organization_code',
        )

    def __init__(self, organization_code):
        self.organization_code = organization_code
       
    def __eq__(self, that):
        if not isinstance(that, self.__class__):
            return False
        self_is_organization_code = self.organization_code is not None
        if self_is_organization_code:
            return self.organization_code == that.organization_code
        else:
            return (self.organization_code is not None and that.organization_code is not None and self.organization_code == that.organization_code)

    def __str__(self):
        if self.organization_code is not None:
            retval = "organization_code-%s" % self.organization_code
        else:
            retval = "unknown organization_code"
        return retval

    def __repr__(self):
        return "Discriminator(%s)" % (self.organization_code)

    def __hash__(self):
        return 1


def add_qr_aes_plugin(config, plugin, organization_code):
    """ プラグイン登録
    :param plugin: an instance of IQRAESPlugin
    :param organization_code: organization's code
    """
    key = Discriminator(organization_code + "-plugin")
    def register():
        logger.info("add_qr_aes_plugin: %r registered for %s" % (plugin, organization_code))
        config.registry.utilities.register([], IQRAESPlugin, str(key), plugin)
    intr = config.introspectable(
        "qr aes plugin", str(key),
        config.object_description(plugin),
        "organization_code=%s" % organization_code
        )
    config.action(key, register, introspectables=[intr], order=QE_AES_CONFIG)

def add_qr_aes_delivery_form_maker(config, maker, organization_code):
    """ ヘルパー登録
    :param maker: an instance of IQRAESFormHelper
    :param organization_code: organization's code
    """
    key = Discriminator(organization_code + "-form-helper")

    def register():
        logger.info("add_qr_aes_form_helper: %r registered for %s" % (maker, organization_code))
        config.registry.utilities.register([], IQRAESDeliveryFormMaker, str(key), maker)

    intr = config.introspectable(
        "qr aes delivery form maker", str(key),
        config.object_description(maker),
        "organization_code=%s" % organization_code
    )
    config.action(key, register, introspectables=[intr], order=QE_AES_CONFIG)
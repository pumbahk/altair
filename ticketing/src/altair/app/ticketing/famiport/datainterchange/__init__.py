def includeme(config):
    from .interfaces import IFamiPortFileManagerFactory
    from .filetransfer import create_ftps_file_sender_from_settings, FamiPortFileManagerFactory
    sender = create_ftps_file_sender_from_settings(config.registry.settings)
    factory = FamiPortFileManagerFactory(sender, 'altair.famiport')
    factory.add_configuration_from_settings('refund', config.registry.settings)
    factory.add_configuration_from_settings('sales', config.registry.settings)
    config.registry.registerUtility(factory, IFamiPortFileManagerFactory)

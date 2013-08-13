def register_codecs():
    from . import cp932_normalized_tilde
    import codecs
    codecs.register(cp932_normalized_tilde.searcher)

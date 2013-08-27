import unicodedata

def NFKC(unistr):
    return unicodedata.normalize('NFKC', unistr)

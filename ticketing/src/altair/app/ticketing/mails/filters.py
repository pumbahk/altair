import unicodedata
from altair.formhelpers.filters import replace_ambiguous

def NFKC(unistr):
    return unicodedata.normalize('NFKC', unistr)

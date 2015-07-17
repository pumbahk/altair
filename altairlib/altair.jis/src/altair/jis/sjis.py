def sjis_iterator(v):
    s = 0
    for c in v:
        if c.__class__ != int:
            c = ord(c)
        if s == 0:
            if (c >= 0x81 and c <= 0x9f) or (c >= 0xe0 and c <= 0xfc):
                s = c << 8
                continue
        else:
            c = s | c
            s = 0
        yield c

def multibyte_in_sjis(v):
    return all(c >= 0x100 for c in sjis_iterator(v.encode('cp932')))

def len_in_sjis(v):
    return sum(2 if c >= 0x100 else 1 for c in sjis_iterator(v.encode('cp932')))

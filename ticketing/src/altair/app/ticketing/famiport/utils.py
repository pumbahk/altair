# -*- coding: utf-8 -*-
import jctconv


def hankaku2zenkaku(text):
    """半角英数字を全角に変換する
    """
    return jctconv.h2z(text, digit=True, ascii=True)


def convert_famiport_kogyo_name_style(text, zenkaku=True, length=40, encoding='cp932', length_error=False):
    """FamiPort用興行名変換処理"""
    if zenkaku:
        text = hankaku2zenkaku(text)
    buf = text.encode(encoding)
    if len(buf) > length and length_error:
        raise ValueError('too long: {}'.format(text))
    for ii in range(len(buf)):
        try:
            return buf[:40-ii].decode(encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    assert False, text


def validate_convert_famiport_kogyo_name_style(*args, **kwds):
    kwds['length_error'] = True
    try:
        convert_famiport_kogyo_name_style(*args, **kwds)
        return True
    except Exception:
        return False

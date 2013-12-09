# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import sys
import os
from functools import partial
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from tssvg import (
    TSSVGEffect, 
    ReplaceMapping, 
)


mapping = {
    "Arial": u"Arial",
    "Arial Black": u"Arial Black",
    "Arial Bold": u"Arial Bold",
    "Arial Bold Italic": u"Arial Bold Italic",
    "Arial Italic": u"Arial Italic",
    "Batang": u"Batang",
    "BatangChe": u"BatangChe",
    "Comic Sans MS": u"Comic Sans MS",
    "Comic Sans MS Bold": u"Comic Sans MS Bold",
    "Courier New": u"Courier New",
    "Courier New Bold": u"Courier New Bold",
    "Courier New Bold Italic": u"Courier New Bold Italic",
    "Courier New Italic": u"Courier New Italic",
    "Dialog.bold": u"Dialog.bold",
    "Dialog.bolditalic": u"Dialog.bolditalic",
    "Dialog.italic": u"Dialog.italic",
    "Dialog.plain": u"Dialog.plain",
    "DialogInput.bold": u"DialogInput.bold",
    "DialogInput.bolditalic": u"DialogInput.bolditalic",
    "DialogInput.italic": u"DialogInput.italic",
    "DialogInput.plain": u"DialogInput.plain",
    "Dotum": u"Dotum",
    "DotumChe": u"DotumChe",
    "Estrangelo Edessa": u"Estrangelo Edessa",
    "Franklin Gothic Medium": u"Franklin Gothic Medium",
    "Franklin Gothic Medium Italic": u"Franklin Gothic Medium Italic",
    "Gautami": u"Gautami",
    "Georgia": u"Georgia",
    "Georgia Bold": u"Georgia Bold",
    "Georgia Bold Italic": u"Georgia Bold Italic",
    "Georgia Italic": u"Georgia Italic",
    "Gulim": u"Gulim",
    "GulimChe": u"GulimChe",
    "Gungsuh": u"Gungsuh",
    "GungsuhChe": u"GungsuhChe",
    "Impact": u"Impact",
    "Kartika": u"Kartika",
    "Latha": u"Latha",
    "Lucida Bright Demibold": u"Lucida Bright Demibold",
    "Lucida Bright Demibold Italic": u"Lucida Bright Demibold Italic",
    "Lucida Bright Italic": u"Lucida Bright Italic",
    "Lucida Bright Regular": u"Lucida Bright Regular",
    "Lucida Console": u"Lucida Console",
    "Lucida Sans Demibold": u"Lucida Sans Demibold",
    "Lucida Sans Demibold": u"Lucida Sans Demibold",
    "Lucida Sans Demibold Roman": u"Lucida Sans Demibold Roman",
    "Lucida Sans Italic": u"Lucida Sans Italic",
    "Lucida Sans Regular": u"Lucida Sans Regular",
    "Lucida Sans Typewriter Bold": u"Lucida Sans Typewriter Bold",
    "Lucida Sans Typewriter Regular": u"Lucida Sans Typewriter Regular",
    "Lucida Sans Unicode": u"Lucida Sans Unicode",
    "MS Gothic": u"ＭＳ ゴシック",
    "MS Mincho": u"ＭＳ 明朝",
    "MS PGothic": u"ＭＳ Ｐゴシック",
    "MS PMincho": u"ＭＳ Ｐ明朝",
    "MS UI Gothic": u"MS UI Gothic",
    "MV Boli": u"MV Boli",
    "Mangal": u"Mangal",
    "Marlett": u"Marlett",
    "Microsoft Sans Serif": u"Microsoft Sans Serif",
    "MingLiU": u"MingLiU",
    "Monospaced.bold": u"Monospaced.bold",
    "Monospaced.bolditalic": u"Monospaced.bolditalic",
    "Monospaced.italic": u"Monospaced.italic",
    "Monospaced.plain": u"Monospaced.plain",
    "NSimSun": u"NSimSun",
    "PMingLiU": u"PMingLiU",
    "Palatino Linotype": u"Palatino Linotype",
    "Palatino Linotype Bold": u"Palatino Linotype Bold",
    "Palatino Linotype Bold Italic": u"Palatino Linotype Bold Italic",
    "Palatino Linotype Italic": u"Palatino Linotype Italic",
    "Raavi": u"Raavi",
    "SansSerif.bold": u"SansSerif.bold",
    "SansSerif.bolditalic": u"SansSerif.bolditalic",
    "SansSerif.italic": u"SansSerif.italic",
    "SansSerif.plain": u"SansSerif.plain",
    "Serif.bold": u"Serif.bold",
    "Serif.bolditalic": u"Serif.bolditalic",
    "Serif.italic": u"Serif.italic",
    "Serif.plain": u"Serif.plain",
    "Shruti": u"Shruti",
    "SimHei": u"SimHei",
    "SimSun": u"SimSun",
    "SimSun-PUA": u"SimSun-PUA",
    "Sylfaen": u"Sylfaen",
    "Symbol": u"Symbol",
    "Tahoma": u"Tahoma",
    "Tahoma Bold": u"Tahoma Bold",
    "Times New Roman": u"Times New Roman",
    "Times New Roman Bold": u"Times New Roman Bold",
    "Times New Roman Bold Italic": u"Times New Roman Bold Italic",
    "Times New Roman Italic": u"Times New Roman Italic",
    "Trebuchet MS": u"Trebuchet MS",
    "Trebuchet MS Bold": u"Trebuchet MS Bold",
    "Trebuchet MS Bold Italic": u"Trebuchet MS Bold Italic",
    "Trebuchet MS Italic": u"Trebuchet MS Italic",
    "Tunga": u"Tunga",
    "Verdana": u"Verdana",
    "Verdana Bold": u"Verdana Bold",
    "Verdana Bold Italic": u"Verdana Bold Italic",
    "Verdana Italic": u"Verdana Italic",
    "Vrinda": u"Vrinda",
    "Webdings": u"Webdings",
    "Wingdings": u"Wingdings",
}
for k in mapping:
    mapping[k] = mapping[k].encode("utf-8")

def convert(familyname, mapping=mapping):
    if familyname in mapping:
        return mapping[familyname]
    else:
        return familyname

target_keys = ["font-family", "-inkscape-font-specification"]

def getapp(mapping=mapping):
    return TSSVGEffect(ReplaceMapping(target_keys, partial(convert, mapping=mapping)))

if __name__ == '__main__':
    e = getapp()
    # e.affect(["./sample.win.xml"])
    e.affect()

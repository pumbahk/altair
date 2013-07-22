# encoding: utf-8

import math
import sys
import struct
import collections

DEFAULT_INITIAL_CAPACITY = 16
MAXIMUM_CAPACITY = 1 << 30
DEFAULT_LOAD_FACTOR = 0.75

class JavaHasher(object):
    def __init__(self, system_encoding=sys.getdefaultencoding()):
        self.system_encoding = system_encoding

    def calculateHashForUnicode(self, uni):
        utf16 = uni.encode("UTF-16BE")
        off = 0
        l = len(utf16)
        h = 0
        while off < l:
            v = struct.unpack(">H", utf16[off:off + 2])[0]
            off += 2
            h = (31 * h + v) & 0xffffffff
        return h

    def __call__(self, obj):
        if isinstance(obj, str):
            return self.calculateHashForUnicode(unicode(obj, self.system_encoding))
        elif isinstance(obj, unicode):
            return self.calculateHashForUnicode(obj)
        raise NotImplemented()

class JavaHashMap(object):
    class Entry(tuple):
        __slot__ = ()

        def __new__(self, key, value, h, prev, next):
            instance = tuple.__new__(self, (key, value))
            instance.h = h
            instance.prev = prev
            instance.next = next
            return instance

        @property
        def key(self):
            return self[0]

        @property
        def value(self):
            return self[1]

    def __init__(self, initial_capacity=DEFAULT_INITIAL_CAPACITY, load_factor=DEFAULT_LOAD_FACTOR, hasher=JavaHasher()):
        if initial_capacity > MAXIMUM_CAPACITY:
            initial_capacity = MAXIMUM_CAPACITY
        if load_factor <= 0 or math.isnan(load_factor):
            raise ValueError("Illegal load factor: " + load_factor)

        capacity = 1
        while capacity < initial_capacity:
            capacity <<= 1

        self.load_factor = load_factor;
        self.threshold = int(capacity * load_factor)
        self.buckets = [None] * capacity

        def hash(obj):
            h = hasher(obj)
            h ^= (h >> 20) ^ (h >> 12)
            return h ^ (h >> 7) ^ (h >> 4)

        self.hasher = hash
        self.mod_count = 0
        self.size = 0

    def index_for(self, h, length):
        return h & (length - 1)

    def rehash(self, new_capacity):
        if len(self.buckets) == MAXIMUM_CAPACITY:
            return
        new_buckets = [None] * new_capacity
        for entry in self.buckets:
            while entry is not None:
                next = entry.next
                i = self.index_for(entry.h, new_capacity)
                entry.next = new_buckets[i]
                new_buckets[i] = entry
                entry = next
        self.buckets = new_buckets
        self.threshold = int(new_capacity * self.load_factor)

    def find_entry(self, key):
        if key is None:
            entry = self.buckets[0]
            while entry is not None:
                if entry.key is None:
                    return entry
                entry = entry.next
        else:
            h = self.hasher(key)
            i = self.index_for(h, len(self.buckets))
            entry = self.buckets[i]
            while entry is not None:
                if entry.h == h and entry.key == key:
                    return entry
                entry = entry.next
        return None

    def __setitem__(self, key, value):
        if key is None:
            entry = self.buckets[0]
            while entry is not None:
                if entry.key is None:
                    old_value = entry.value
                    new_entry = self.Entry(key, value, 0, entry.prev, entry.next)
                    if entry.prev is None:
                        self.buckets[0] = new_entry
                    else:
                        entry.prev.next = new_entry
                    if entry.next is not None:
                        entry.next.prev = new_entry
                    entry.value = value
                    return old_value
                entry = entry.next

            new_entry = self.Entry(key, value, h, None, self.buckets[0])
            if new_entry.next is not None:
                new_entry.next.prev = entry
            self.buckets[0] = new_entry

            if self.size >= self.threshold:
                self.rehash(2 * len(self.buckets))
            self.size += 1
        else:
            h = self.hasher(key)
            i = self.index_for(h, len(self.buckets))
            entry = self.buckets[i]
            while entry is not None:
                if entry.h == h and entry.key == key:
                    old_value = entry.value
                    new_entry = self.Entry(key, value, h, entry.prev, entry.next)
                    if entry.prev is None:
                        self.buckets[i] = new_entry
                    else:
                        entry.prev.next = new_entry
                    if entry.next is not None:
                        entry.next.prev = new_entry
                    return old_value
                entry = entry.next

            self.mod_count += 1

            new_entry = self.Entry(key, value, h, None, self.buckets[i])
            if new_entry.next is not None:
                new_entry.next.prev = entry
            self.buckets[i] = new_entry

            if self.size >= self.threshold:
                self.rehash(2 * len(self.buckets))
            self.size += 1
        return None

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        entry = self.find_entry(key)
        return default if entry is None else entry.value

    def iteritems(self):
        i = 0
        while i < len(self.buckets):
            entry = self.buckets[i]
            while entry is not None:
                yield entry
                entry = entry.next
            i += 1

    def iterkeys(self):
        for entry in self.iteritems():
            yield entry.key

    def __iter__(self):
        return self.iterkeys()


def convert(text, *maps, **ops):
    """ 変換マップを指定して、文字列を変換します。
    追加の変換マップを dict や tuple で簡単に利用できます。
    処理をスキップする文字を指定することが出来ます。

    args:
        text: 変換元のテキスト。unicode を必要とします。
        maps: 変換マップの指定。tuple, dict または tuple を返す関数（callable オブジェクト）で指定。
                    マップは指定された順序に実行されます。
        skip: 変換しない除外文字の指定。tuple または文字列で指定
                    tuple で指定すると各要素を除外。文字列で指定すると含まれる全ての文字を除外。
    return:
        converted unicode string

    built-in maps:
        H_SPACE (HS): スペースを半角に統一
        H_NUM (HN): 数字を半角に統一
        H_ALPHA (HA): 英字を半角に統一
        H_KIGO (HKG): ASCII記号を半角に統一
        H_KATA (HK): カタカナを半角カタカナに統一
        H_ASCII (HAC): アスキー文字を半角に統一（スペースを除く）（＝H_NUM + H_ALPHA + H_KIGO）
        Z_SPACE (ZS): スペースを全角に統一
        Z_NUM (ZN): 数字を全角に統一
        Z_ALPHA (ZA): 英字を全角に統一
        Z_KIGO (ZKG): ASCII記号を全角に統一
        Z_KATA (ZK): カタカナを全角に統一
        Z_ASCII (ZAC): アスキー文字を全角に統一（スペースを除く）（＝Z_NUM + Z_ALPHA + Z_KIGO）
        HIRA2KATA (H2K): ひらがなをカタカナに変換
        KATA2HIRA (K2H): カタカナをひらがなに変換
    """
    if "skip" in ops:
        skip = ops["skip"]
        if isinstance(skip, basestring):
            skip = tuple(skip)
        def replace(text, fr, to):
            return text if fr in skip else text.replace(fr, to)
    else:
        def replace(text, fr, to):
            return text.replace(fr, to)

    for map in maps:
        if callable(map):
            map = map()
        elif isinstance(map, dict):
            map = map.items()
        for fr, to in map:
            text = replace(text, fr, to)

    return text

H_SPACE = HS = ((u"　",u" "),)
H_NUM = HN = (
    (u"０",u"0"),(u"１",u"1"),(u"２",u"2"),(u"３",u"3"),(u"４",u"4"),
    (u"５",u"5"),(u"６",u"6"),(u"７",u"7"),(u"８",u"8"),(u"９",u"9"),
    )
H_ALPHA = HA = (
    (u"ａ",u"a"),(u"ｂ",u"b"),(u"ｃ",u"c"),(u"ｄ",u"d"),(u"ｅ",u"e"),
    (u"ｆ",u"f"),(u"ｇ",u"g"),(u"ｈ",u"h"),(u"ｉ",u"i"),(u"ｊ",u"j"),
    (u"ｋ",u"k"),(u"ｌ",u"l"),(u"ｍ",u"m"),(u"ｎ",u"n"),(u"ｏ",u"o"),
    (u"ｐ",u"p"),(u"ｑ",u"q"),(u"ｒ",u"r"),(u"ｓ",u"s"),(u"ｔ",u"t"),
    (u"ｕ",u"u"),(u"ｖ",u"v"),(u"ｗ",u"w"),(u"ｘ",u"x"),(u"ｙ",u"y"),(u"ｚ",u"z"),
    (u"Ａ",u"A"),(u"Ｂ",u"B"),(u"Ｃ",u"C"),(u"Ｄ",u"D"),(u"Ｅ",u"E"),
    (u"Ｆ",u"F"),(u"Ｇ",u"G"),(u"Ｈ",u"H"),(u"Ｉ",u"I"),(u"Ｊ",u"J"),
    (u"Ｋ",u"K"),(u"Ｌ",u"L"),(u"Ｍ",u"M"),(u"Ｎ",u"N"),(u"Ｏ",u"O"),
    (u"Ｐ",u"P"),(u"Ｑ",u"Q"),(u"Ｒ",u"R"),(u"Ｓ",u"S"),(u"Ｔ",u"T"),
    (u"Ｕ",u"U"),(u"Ｖ",u"V"),(u"Ｗ",u"W"),(u"Ｘ",u"X"),(u"Ｙ",u"Y"),(u"Ｚ",u"Z"),
    )
H_SIGN = HKG = (
    (u"．",u"."),(u"，",u","),(u"！",u"!"),(u"？",u"?"),(u"”",u'"'),
    (u"’",u"'"),(u"‘",u"`"),(u"＠",u"@"),(u"＿",u"_"),(u"：",u":"),
    (u"；",u";"),(u"＃",u"#"),(u"＄",u"$"),(u"％",u"%"),(u"＆",u"&"),
    (u"（",u"("),(u"）",u")"),(u"‐",u"-"),(u"＝",u"="),(u"＊",u"*"),
    (u"＋",u"+"),(u"－",u"-"),(u"／",u"/"),(u"＜",u"<"),(u"＞",u">"),
    (u"［",u"["),(u"￥",u"\\"),(u"］",u"]"),(u"＾",u"^"),(u"｛",u"{"),
    (u"｜",u"|"),(u"｝",u"}"),(u"～",u"~")
    )
H_KATA = HK = (
    (u"ァ",u"ｧ"),(u"ィ",u"ｨ"),(u"ゥ",u"ｩ"),(u"ェ",u"ｪ"),(u"ォ",u"ｫ"),
    (u"ッ",u"ｯ"),(u"ャ",u"ｬ"),(u"ュ",u"ｭ"),(u"ョ",u"ｮ"),
    (u"ガ",u"ｶﾞ"),(u"ギ",u"ｷﾞ"),(u"グ",u"ｸﾞ"),(u"ゲ",u"ｹﾞ"),(u"ゴ",u"ｺﾞ"),
    (u"ザ",u"ｻﾞ"),(u"ジ",u"ｼﾞ"),(u"ズ",u"ｽﾞ"),(u"ゼ",u"ｾﾞ"),(u"ゾ",u"ｿﾞ"),
    (u"ダ",u"ﾀﾞ"),(u"ヂ",u"ﾁﾞ"),(u"ヅ",u"ﾂﾞ"),(u"デ",u"ﾃﾞ"),(u"ド",u"ﾄﾞ"),
    (u"バ",u"ﾊﾞ"),(u"ビ",u"ﾋﾞ"),(u"ブ",u"ﾌﾞ"),(u"ベ",u"ﾍﾞ"),(u"ボ",u"ﾎﾞ"),
    (u"パ",u"ﾊﾟ"),(u"ピ",u"ﾋﾟ"),(u"プ",u"ﾌﾟ"),(u"ペ",u"ﾍﾟ"),(u"ポ",u"ﾎﾟ"),
    (u"ヴ",u"ｳﾞ"),
    (u"ア",u"ｱ"),(u"イ",u"ｲ"),(u"ウ",u"ｳ"),(u"エ",u"ｴ"),(u"オ",u"ｵ"),
    (u"カ",u"ｶ"),(u"キ",u"ｷ"),(u"ク",u"ｸ"),(u"ケ",u"ｹ"),(u"コ",u"ｺ"),
    (u"サ",u"ｻ"),(u"シ",u"ｼ"),(u"ス",u"ｽ"),(u"セ",u"ｾ"),(u"ソ",u"ｿ"),
    (u"タ",u"ﾀ"),(u"チ",u"ﾁ"),(u"ツ",u"ﾂ"),(u"テ",u"ﾃ"),(u"ト",u"ﾄ"),
    (u"ナ",u"ﾅ"),(u"ニ",u"ﾆ"),(u"ヌ",u"ﾇ"),(u"ネ",u"ﾈ"),(u"ノ",u"ﾉ"),
    (u"ハ",u"ﾊ"),(u"ヒ",u"ﾋ"),(u"フ",u"ﾌ"),(u"ヘ",u"ﾍ"),(u"ホ",u"ﾎ"),
    (u"マ",u"ﾏ"),(u"ミ",u"ﾐ"),(u"ム",u"ﾑ"),(u"メ",u"ﾒ"),(u"モ",u"ﾓ"),
    (u"ヤ",u"ﾔ"),(u"ユ",u"ﾕ"),(u"ヨ",u"ﾖ"),
    (u"ラ",u"ﾗ"),(u"リ",u"ﾘ"),(u"ル",u"ﾙ"),(u"レ",u"ﾚ"),(u"ロ",u"ﾛ"),
    (u"ワ",u"ﾜ"),(u"ヲ",u"ｦ"),(u"ン",u"ﾝ"),
    (u"。",u"｡"),(u"、",u"､"),(u"゛",u"ﾞ"),(u"゜",u"ﾟ"),
    (u"「",u"｢"),(u"」",u"｣"),(u"・",u"･"),(u"ー",u"ｰ"),
    )
HIRA2KATA = (
    (u"ぁ",u"ァ"),(u"ぃ",u"ィ"),(u"ぅ",u"ゥ"),(u"ぇ",u"ェ"),(u"ぉ",u"ォ"),
    (u"っ",u"ッ"),(u"ゃ",u"ャ"),(u"ゅ",u"ュ"),(u"ょ",u"ョ"),
    (u"が",u"ガ"),(u"ぎ",u"ギ"),(u"ぐ",u"グ"),(u"げ",u"ゲ"),(u"ご",u"ゴ"),
    (u"ざ",u"ザ"),(u"じ",u"ジ"),(u"ず",u"ズ"),(u"ぜ",u"ゼ"),(u"ぞ",u"ゾ"),
    (u"だ",u"ダ"),(u"ぢ",u"ヂ"),(u"づ",u"ヅ"),(u"で",u"デ"),(u"ど",u"ド"),
    (u"ば",u"バ"),(u"び",u"ビ"),(u"ぶ",u"ブ"),(u"べ",u"ベ"),(u"ぼ",u"ボ"),
    (u"ぱ",u"パ"),(u"ぴ",u"ピ"),(u"ぷ",u"プ"),(u"ぺ",u"ペ"),(u"ぽ",u"ポ"),
    (u"ヴ",u"ヴ"),
    (u"あ",u"ア"),(u"い",u"イ"),(u"う",u"ウ"),(u"え",u"エ"),(u"お",u"オ"),
    (u"か",u"カ"),(u"き",u"キ"),(u"く",u"ク"),(u"け",u"ケ"),(u"こ",u"コ"),
    (u"さ",u"サ"),(u"し",u"シ"),(u"す",u"ス"),(u"せ",u"セ"),(u"そ",u"ソ"),
    (u"た",u"タ"),(u"ち",u"チ"),(u"つ",u"ツ"),(u"て",u"テ"),(u"と",u"ト"),
    (u"な",u"ナ"),(u"に",u"ニ"),(u"ぬ",u"ヌ"),(u"ね",u"ネ"),(u"の",u"ノ"),
    (u"は",u"ハ"),(u"ひ",u"ヒ"),(u"ふ",u"フ"),(u"へ",u"ヘ"),(u"ほ",u"ホ"),
    (u"ま",u"マ"),(u"み",u"ミ"),(u"む",u"ム"),(u"め",u"メ"),(u"も",u"モ"),
    (u"や",u"ヤ"),(u"ゆ",u"ユ"),(u"よ",u"ヨ"),
    (u"ら",u"ラ"),(u"り",u"リ"),(u"る",u"ル"),(u"れ",u"レ"),(u"ろ",u"ロ"),
    (u"わ",u"ワ"),(u"を",u"ヲ"),(u"ん",u"ン"),
    )

Z_SPACE = ZS = ((u" ",u"　"),)
Z_NUM = ZN = lambda: ((h, z) for z, h in H_NUM)
Z_ALPHA = ZA = lambda: ((h, z) for z, h in H_ALPHA)
Z_SIGN = ZKG = lambda: ((h, z) for z, h in H_SIGN)
Z_KATA = ZK = lambda: ((h, z) for z, h in H_KATA)
KATA2HIRA = lambda: ((k, h) for h, k in HIRA2KATA)
H_ASCII = HAC = lambda: ((fr, to) for map in (H_ALPHA, H_NUM, H_SIGN) for fr, to in map)
Z_ASCII = ZAC = lambda: ((h, z) for z, h in H_ASCII())

def han2zen(text):
    return convert(text, Z_NUM, Z_ALPHA, Z_SIGN, Z_KATA)

import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
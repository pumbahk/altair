# -*- coding: utf-8 -*-
import lxml


class FamiPortFakeFactory(object):
    xml = ''

    @classmethod
    def parse(cls, text, *args, **kwds):
        txt = text.encode('cp932')
        return lxml.etree.XML(txt)

    @classmethod
    def create(cls, *args, **kwds):
        return cls.parse(cls.xml.decode('utf8'))

    @classmethod
    def match(cls, text, *args, **kwds):
        original = cls.create(*args, **kwds)
        other = lxml.etree.XML(text)
        return original == other


class FamiPortReservationInquiryResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<replyClass>1</replyClass>
<replyCode>00</replyCode>
<barCodeNo>4110000000006</barCodeNo>
<totalAmount>00000670</totalAmount>
<ticketPayment>00000000</ticketPayment>
<systemFee>00000500</systemFee>
<ticketingFee>00000170</ticketingFee>
<ticketCountTotal>1</ticketCountTotal>
<ticketCount>1</ticketCount>
<kogyoName>サンプル興行</kogyoName>
<koenDate>201505011000</koenDate>
<nameInput>0</nameInput>
<phoneInput>0</phoneInput>
</FMIF>
"""


class FamiPortPaymentTicketingResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>099999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>4310000000002</barCodeNo>
<orderId>430000000002</orderId>
<replyClass>3</replyClass>
<replyCode>00</replyCode>
<playGuideId>00001</playGuideId>
<playGuideName>クライアント１</playGuideName>
<exchangeTicketNo>4310000000002</exchangeTicketNo>
<totalAmount>00000200</totalAmount>
<ticketPayment>00000000</ticketPayment>
<systemFee>00000000</systemFee>
<ticketingFee>00000200</ticketingFee>
<ticketCountTotal>5</ticketCountTotal>
<ticketCount>5</ticketCount>
<kogyoName>ａｂｃｄｅｆｇｈｉｊ１２３４５６７８９０</kogyoName>
<koenDate>999999999999</koenDate>
<ticket>
<barCodeNo>1234567890019</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890026</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890033</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890040</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890057</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
</FMIF>
"""


class FamiPortPaymentTicketingCompletionResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>099999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>6010000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
"""


class FamiPortPaymentTicketingCancelResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>099999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>3300000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
"""


class FamiPortInformationResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
    <resultCode>00</resultCode>
    <infoKubun>0</infoKubun>
    <infoMessage>テスト1
テスト2
テスト3
テスト4
テスト5
テスト6
テスト7
テスト8
テスト9
テスト10
テスト11
テスト12
テスト13
テスト14
テスト15
テスト16
テスト17
テスト18
テスト19
テスト20
テスト21
テスト22
テスト23</infoMessage>
</FMIF>
"""


class FamiPortCustomerResponseFakeFactory(FamiPortFakeFactory):
    xml = """<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<replyCode>00</replyCode>
<name>k9DUstJ8MjSxS5vCrHoXsDwUnlz6oUt9oBAD7aAVIJBXWFvLkbehVbFSejR8dFDpmfpeg0/+OvSEC6JWNhukadAwwt8Fd26uyZzykiTMwVQ=</name>
<memberId>lVdX1ezHs1NTaoTSLXR6SAYojrjWLzvgwgADleHELvQ=</memberId>
<address1>k9DUstJ8MjSxS5vCrHoXsEJE3WJ6M2Js7/U/bn0xdnnjQPJsT/lpdofLF2fyld8IKNskWqmQBaT538Z54GDc+A/gXkwY91eDwJ43i8VZ4jQKX2+cx9bRTu0IKgF3eCcGgAWUZ6LBOAQu17LMb/Y5auHbDcznH1yfNTfuRTWAFDcv+JFtJKAjbKXS3/vu9ISUCt7u4JzpBln9oYXHRYoAGIVZTDVmgdco9v51kDHugnM=</address1>
<address2>k9DUstJ8MjSxS5vCrHoXsEJE3WJ6M2Js7/U/bn0xdnnjQPJsT/lpdofLF2fyld8IKNskWqmQBaT538Z54GDc+A/gXkwY91eDwJ43i8VZ4jQKX2+cx9bRTu0IKgF3eCcGgAWUZ6LBOAQu17LMb/Y5auHbDcznH1yfNTfuRTWAFDcv+JFtJKAjbKXS3/vu9ISUCt7u4JzpBln9oYXHRYoAGIVZTDVmgdco9v51kDHugnM=</address2>
<identifyNo>1234567890123456</identifyNo>
</FMIF>
"""

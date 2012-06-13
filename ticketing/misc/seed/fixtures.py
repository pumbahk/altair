# encoding: utf-8

from random import randint, choice
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from itertools import chain
from fixture import rel, auto, Data as _Data, DataSuite, DataWalker
from collections import OrderedDict
import logging
import hashlib

logger = logging.getLogger('fixtures')

SALT = '5t&a'; # gotanda

stock_type_pairs = [
    (u'S席', 0),
    (u'A席', 0),
    (u'B席', 0),
    (u'自由席', 1),
    (u'駐車券', 1),
    (u'ノベルティ', 1),
    ]

stock_type_combinations = {
    u'S席大人': [
        (u'S席', 5000),
        ],
    u'S席子供': [
        (u'S席', 3000),
        ],
    u'A席大人': [
        (u'A席', 4000),
        ],
    u'A席子供': [
        (u'A席', 3000),
        ],
    u'B席大人': [
        (u'B席', 3000),
        ],
    u'B席子供': [
        (u'B席', 2000),
        ],
    u'自由席': [
        (u'自由席', 1000),
        ],
    u'S席大人+駐車券': [
        (u'S席', 5000),
        (u'駐車券', 5000),
        ],
    u'A席大人+駐車券': [
        (u'A席', 4000),
        (u'駐車券', 5000),
        ],
    u'B席大人+駐車券': [
        (u'B席', 3000),
        (u'駐車券', 5000),
        ],
    u'自由席+駐車券': [
        (u'自由席', 1000),
        (u'駐車券', 5000),
        ],
    u'S席大人+ノベルティ': [
        (u'S席', 5000),
        (u'ノベルティ', 0),
        ],
    u'A席大人+ノベルティ': [
        (u'A席', 4000),
        (u'ノベルティ', 0),
        ],
    u'B席大人+ノベルティ': [
        (u'B席', 3000),
        (u'ノベルティ', 0),
        ],
    u'自由席+ノベルティ': [
        (u'自由席', 1000),
        (u'ノベルティ', 0),
        ],
    }

event_names = [
    u'''2012 ANAオープンゴルフトーナメント''',
    u'''2012 SHINHWA GRAND TOUR IN JAPAN "THE RETURN"''',
    u'''2012 ディズニー・ライブ!''',
    u'''2012 ダンロップフェニックストーナメント''',
    u'''2012 ディズニー・オン・アイス「ミッキー・ミニーのプリンセス&ヒーロー」''',
    u'''2012年国立ボリショイサーカス''',
    u'''40th Anniversary 天童よしみコンサート2012''',
    u'''AI 「INDEPENDENT」TOUR 2012''',
    u'''ANDY 除隊ファンミーティング''',
    u'''ANIMAX MUSIX 2012''',
    u'''BNP パリバ デビスカップ 2012 ワールドグループ''',
    u'''Disney Live! Mickey's Music Party!! (ディズニー・ライブ! 英語公演)''',
    u'''FIVB 女子バレーボールワールドグランプリ2012 大阪大会''',
    u'''FUJITSU Presents N響「第九」Special Concert''',
    u'''Girl's Day Party in Zepp''',
    u'''JAPANゴルフツアー開幕戦 東建ホームメイトカップ''',
    u'''K-POP ALL STAR CONCERT 第26回ゴールデンディスク賞授賞式''',
    u'''K-POP GOOD FRIENDS LIVE 2012 IN TOKYO''',
    u'''LOTTE presents THE ICE 2012''',
    u'''LUVandSOUL 「道 ～Don't Look Back In Anger ～ TOUR2012」''',
    u'''Le Velvets "Here we come!!!!!"''',
    u'''Live Dimensional-2012 -24-''',
    u'''MCountdown Hello Japan ～MCountdown One Asia Tour 2012～''',
    u'''NHK 交響楽団 ベートーヴェン「第9」演奏会''',
    u'''OTODAMA'11-'12 〜ヤングライオン編〜''',
    u'''Shin Jae 韓国ドラマO.S.T K-POP LIVE CONCERT''',
    u'''TEENTOP TALK & LIVE''',
    u'''TEENTOP Zepp Tour 2012''',
    u'''THE TOUR OF MISIA JAPAN SOUL QUEST GRAND FINALE 2012''',
    u'''TOKYO FM 夢の第九コンサート2012''',
    u'''TOKYO GAME SHOW 2012''',
    u'''TOSHIKI KADOMATSU 30th Anniversary Performance 2012 -Winter-''',
    u"""TUBE LIVE AROUND 2012 Keep On Smilin'""",
    u'''Tポイントレディス ゴルフトーナメント''',
    u'''Welcome to the Block "NANRINA CONCERT"''',
    u'''YAMATO World Tour Special Edition NIPPON BEAT''',
    u'''YUKI tour"MEGAPHONIC"2012''',
    u'''bjリーグ 大阪エヴェッサ''',
    u'''w-inds. 10th Anniversary BEST LIVE TOUR 2012''',
    u'''第14回東京03単独公演「後手中の後手」''',
    u'''第21回 日本シニアオープンゴルフ選手権競技''',
    u'''第30回 大王製紙エリエール レディスオープン''',
    u'''第42回 コカ・コーラ東海クラシック''',
    u'''第42回 マンシングウェアレディース東海クラシック''',
    u'''第44回 日本女子オープンゴルフ選手権競技''',
    u'''第61回 黒鷲旗全日本男女選抜バレーボール大会''',
    u'''第76回 日本オープンゴルフ選手権競技''',
    u'''第7回 スタジオアリス女子オープン''',
    u'''第80回日本プロゴルフ選手権大会日清カップヌードル杯''',
    u'''「au by KDDI」 presents オンタマカーニバル2012''',
    u'''前川 清・秋元順子特別公演''',
    u'''東レ パン・パシフィック・オープンテニストーナメント''',
    u'''東京03 第13回東京03単独公演『図星中の図星』''',
    u'''平成23年度 松竹特別公演 松竹喜劇まつり''',
    u'''平成24年大相撲三月場所''',
    u'''誕生25周年記念 ドラゴンクエスト展''',
    u'''炎の人''',
    u'''久石譲 Classics vol.4''',
    u'''久石譲&新日本フィル・ワールド・ドリーム・オーケストラ ～Love Songs～''',
    u'''エンロン''',
    u'''岡本知高 Concerto del Sopranista 2012''',
    u'''長嶋茂雄 INVITATIONAL セガサミーカップゴルフトーナメント''',
    u'''安藤裕子 LIVE 2012 「勘違い」''',
    u'''西本智実 指揮 スミ・ジョー イン・コンサート オーケストラ:ラトビア国立交響楽団''',
    u'''西本智実 指揮 クリスマス・アダージョ''',
    u'''西本智実 指揮 ベラルーシ国立交響楽団 ピアノ:アレクサンダー・ルビャンツェフ''',
    u'''美輪明宏 音楽会 ≪愛≫ L'AMOUR 2012''',
    u'''新居昭乃 弾き語り LIVE TOUR 2012 "Little Piano vol.3"''',
    u'''清水和音 ショパン!ショパン!ショパン!''',
    u'''上松美香 クリスマス アルパ・コンサート 2012''',
    u'''江原啓之 新春講演会 〜今必要なメッセージ〜 江原啓之 しあわせ講演会(群馬) ''',
    u'''マキシム ピアノ・ソロ ジャパン・ツアー 2012''',
    u'''ダイハツ クーザ大阪公演''',
    u'''下田聖子 ピアノリサイタル ロマン レパートリー ～リストの大いなる愛と夢～''',
    u'''上松美香 アルパ・コンサート 2012''',
    u'''前橋汀子 華麗なるコンチェルト～演奏活動50周年コンサート''',
    u'''ブラスト!2012''',
    u'''コン・ユ10周年記念公演''',
    u'''卒フェス2012 〜サクラサクトキトビラアク〜in富士急ハイランド''',
    u'''マイナビABCチャンピオンシップゴルフトーナメント''',
    u'''アマデウス''',
    u'''コッペリア''',
    u'''ソ・ジソブ''',
    u'''春風亭小朝 独演会''',
    u'''葉加瀬太郎 コンサートツアー2012 「ザ・ベスト・オブ 葉加瀬太郎」''',
    u'''葉加瀬太郎 クラシックシアターII''',
    u'''ソ・ジソブ 日本公式ファンクラブ1周年記念!2012 ファンミーティング in 東京''',
    u'''佐々木秀実 ドラマティックシャンソンライブ2012 ～まるでお芝居のように～''',
    u'''明治座創業140周年記念 石川さゆり40周年記念 石川さゆり特別公演''',
    u'''明治座創業140周年記念 黒蜥蜴''',
    u'''明治座創業140周年記念 早乙女太一特別公演''',
    u'''明治座創業140周年記念 東儀秀樹コンサート''',
    u'''明治座創業140周年記念 藤あや子コンサート''',
    u'''明治座創業140周年記念 春まつりスペシャル  島津亜矢コンサート 曙光 夜明けの光 〜劇場版スペシャル〜''',
    u'''明治座創業140周年記念 春まつりスペシャル 吉田兄弟 和の祭典''',
    u'''明治座創業140周年記念 春まつりスペシャル 細川たかし 長山洋子 コンサート''',
    u'''明治座創業140周年記念 春まつりスペシャル 美川憲一コンサート''',
    u'''明治座創業140周年記念 女たちの忠臣蔵''',
    u'''明治座創業140周年記念 五木ひろし特別公演''',
    u'''明治座創業140周年記念 春まつりスペシャル  明治座 春の落語会''',
    u'''後藤真希「G-Emotion FINAL」''',
    u'''木下グループ STARS ON ICE JAPAN TOUR 2012 ''',
    u'''フェドカップ by BNPパリバ 2012''',
    u'''錦秋特別公演 芯 2012''',
    u'''ソン・ヨルム ピアノ・リサイタル''',
    u'''木下グループpresents カーニバル・オン・アイス2012''',
    u'''ヴィッセル神戸''',
    u'''楽天イーグルス''',
    u'''東京ランウェイ 2012 S/S TOKYO RUNWAY 2012 Spring / Summer''',
    u'''ヴィッセル神戸 vs ガンバ大阪''',
    u'''パナソニック杯 第66回毎日甲子園ボウル''',
    u'''松竹花形歌舞伎 秋季公演''',
    u'''コマツオープン2012''',
    u'''ヴィッセル神戸VS清水エスパルス''',
    u'''大阪エヴェッサvs大分ヒートデビルズ''',
    u'''楽天イーグルスvs埼玉西武ライオンズ''',
    u'''「海辺のカフカ」''',
    u'''ニチレイレディス''',
    u'''相田みつを美術館 第48回企画展 夏休み特集 子どもへのまなざし -トマトとメロン-''',
    u'''ボローニャ歌劇場 「清教徒」''',
    u'''劇団朱雀特別公演 早乙女太一''',
    u'''ボローニャ歌劇場 「カルメン」''',
    u'''ボローニャ歌劇場 「エルナーニ」''',
    u'''クリス・ボッティ ジャパンツアー 2012 Chris Botti Japan Tour 2012''',
    u'''クリス・ボッティ ジャパンツアー2012 IMPRESSIONS Chris Botti Japan Tour 2012 -IMPRESSIONS-''',
    u'''明治座十一月公演 出逢いに感謝…35周年 川中美幸特別公演''',
    u'''新イタリア合奏団&アンドレア・グリミネッリ''',
    u'''キヤノンオープン2012''',
    u'''沖縄県伝統芸能公演''',
    u'''ブルーマングループ IN 東京''',
    u'''ブルーマングループ IN 東京 2012年''',
    u'''木下グループカップ フィギュアスケート JAPAN OPEN 2012 3地域対抗戦 ''',
    u'''ディズニー・ライブ!''',
    u'''ディズニー・ライブ! 「ミッキー&ミニーのスターをさがせ!!」''',
    u'''スマイルプリキュア! ミュージカルショー''',
    u'''秋元順子コンサート2012''',
    u'''舟木一夫コンサート2012''',
    u'''キッズ・パラダイス2012『トミカ博 in NAGOYA』〜出動せよ!まちをまもる緊急車両!!!〜''',
    u'''ペレス・プラード楽団''',
    u'''ナイジェル・ケネディ presents バッハ meets ファッツ・ウォーラー''',
    u'''エジプト考古学博物館 所蔵 ツタンカーメン展 〜黄金の秘宝と少年王の真実〜''',
    u'''東日本大震災復興支援 ゴールドリボン基金+世界の子どもにワクチンを チャリティー企画 市川亀治郎×三響會特別公演 〜伝統芸能の今2012〜''',
    u'''山本寛斎プロデュース!スーパー元気ステージYAY!''',
    u'''三大ピアノ協奏曲の饗宴''',
    u'''≪先行≫東京ランウェイ 2012 S/S TOKYO RUNWAY 2012 Spring / Summer''',
    u'''横浜みなとみらいホール 2012オープニング・コンサート ウィーン・シュトラウス・フェスティヴァル・オーケストラ with 鈴木慶江&水口聡''',
    u'''ロックロックこんにちは!Ver.15 ANNIVERSARY 怪人 十五少年反抗機 ''',
    u'''フレデリック・バック展/L'Homme qui Plantait des Arbres ''',
    u'''プレナスなでしこリーグ2012''',
    u'''名曲アルバムコンサート2012「聖なるクリスマス」''',
    u'''名曲アルバムコンサート2012「ピアノ名曲ベストコレクション」''',
    u'''【楽天特別販売】ダイハツ クーザ大阪公演''',
    u'''アンジェラ・ゲオルギュー ガラ・コンサート''',
    u'''大エルミタージュ美術館展 世紀の顔・西欧絵画の400年''',
    u'''ディズニー・オン・アイス 「オールスターカーニバル」''',
    u'''ダイヤモンドカップゴルフ2012''',
    u'''松下奈緒コンサートツアー2012 for me''',
    u'''シルク・ドゥ・ソレイユ「ZED (ゼッド)TM」Presented by JCB ''',
    u'''音楽劇「醒めながら見る夢」''',
    u'''サントリーレディスオープン 2012''',
    u'''上松美香アルパ・コンサート 2012 AMANECER -夜明け-''',
    u'''ブラッド・メルドー・トリオ in Tokyo''',
    u'''「コクリコ坂から」公開記念 手嶌葵 コンサート''',
    u'''東日本大震災復興チャリティ ドリームテニスARIAKE''',
    u'''コンスタンチン・リフシッツ ピアノリサイタル''',
    u'''錦織健プロデュース・オペラ ロッシーニ「セビリアの理髪師」''',
    u'''ヤマハレディースオープン葛城''',
    u'''東北楽天ゴールデンイーグルス''',
    u'''ディズニー・オン・クラシック 〜まほうの夜の音楽会 2012 Journey 〜夢に向かって''',
    u'''プレナスなでしこリーグカップ2012 第3節''',
    u'''東北楽天ゴールデンイーグルス6月開催試合''',
    u'''アレクサンダー・ルビャンツェフ ピアノ・リサイタル''',
    u'''フェルメールからのラブレター展 コミュニケーション:17世紀オランダ絵画から読み解く人々のメッセージ''',
    u'''イングリット・フジコ・ヘミング ピアノ・ソロ・リサイタル 2012''',
    u'''加山雄三ホールコンサートツアー"若大将・湘南FOREVER"''',
    u'''イングリット・フジコ・ヘミング&ラトビア国立交響楽団''',
    u'''イングリット・フジコ・ヘミング&ベラルーシ国立交響楽団''',
    u'''トリニティ・アイリッシュ・ダンス''',
    u'''丸美屋食品ミュージカル「アニー」''',
    u'''オリジナル・ドローイング・ショー ～The Cube～''',
    u'''グローリー・ゴスペル・シンガーズ クリスマス☆ゴスペル2012''',
    u'''デューク・エリントン・オーケストラ ジャパンツアー2012''',
    u'''ブロードウェイミュージカル『ジキル&ハイド』''',
    u'''ディズニー・オン・アイス「ミッキー&ミニーのプリンセス&ヒーロー」埼玉公演''',
    u'''ラ・フォル・ジュルネ・オ・ジャポン2012''',
    u'''【楽天特別販売】秋元順子コンサート2012''',
    u'''【未使用】シルク・ドゥ・ソレイユ「ZED (ゼッド)TM」Presented by JCB''',
    u'''トロカデロ・デ・モンテカルロバレエ団''',
    u'''恵比寿マスカッツアジアツアー凱旋公演 「そうだ!みんなで中野サンプラザに行こう」''',
    u'''【特別販売】コンスタンチン・リフシッツ ピアノリサイタル''',
    u'''ブリヂストンオープンゴルフトーナメント2012''',
    u'''上松美香アルパ・ニューイヤーコンサート2013''',
    u'''ブロードウェイミュージカル『キャバレー』''',
    u'''上原彩子ピアノ・リサイタル「展覧会の絵」''',
    u'''中京テレビ・ブリヂストンレディスオープン''',
    u'''ツタンカーメン展〜黄金の秘宝と少年王の真実〜''',
    u'''ザ・レジェンド・チャリティプロアマトーナメント''',
    u'''ワールドレディスチャンピオンシップサロンパスカップ''',
    u'''アジアパシフィックオープンゴルフチャンピオンシップ パナソニックオープン''',
    u'''ワールドレディスチャンピオンシップサロンパスカップ2012''',
    u'''ディズニー・オン・アイス「ミッキー・ミニーのプリンセス&ヒーロー」''',
    u'''楽天・ジャパン・オープン・テニス・チャンピオンシップス2012''',
    ]

site_names = [
    u'Bunkamuraオーチャードホール',
    u'NHKホール',
    u'SHIBUYA-AX',
    u'Zepp Tokyo',
    u'iichiko総合文化センター',
    u'渋谷C.C.Lemonホール',
    u'国技館',
    u'明治座',
    u'利府町 グランディ・21 (宮城県総合体育館)',
    u'なかのZERO 大ホール',
    u'両国国技館',
    u'博品館劇場',
    u'国立能楽堂',
    u'山野ホール',
    u'新潟テルサ',
    u'日本武道館',
    u'日本青年館',
    u'會津風雅堂',
    u'東京体育館',
    u'浅草公会堂',
    u'王子ホール',
    u'浪切ホール 大ホール',
    u'山形テルサ テルサホール',
    u'倉敷市民会館',
    u'大阪城ホール',
    u'山形県民会館',
    u'日比谷公会堂',
    u'横浜アリーナ',
    u'紀尾井ホール',
    u'長崎市公会堂',
    u'紀南文化会館 大ホール',
    u'ぐんまアリーナ',
    u'なみはやドーム',
    u'よみうりホール',
    u'パストラルかぞ',
    u'坂戸市文化会館',
    u'大阪府立体育館',
    u'守口市民体育館',
    u'愛知県芸術劇場',
    u'有明コロシアム',
    u'横浜文化体育館',
    u'町田市民ホール',
    u'神戸中央体育館',
    u'阪神甲子園球場',
    u'青森市文化会館',
    u'前橋市文化会館 大ホール',
    u'文化パルク城陽 プラムホール',
    u'立川市市民会館 (アミューたちかわ) 大ホール',
    u'ゆうぽうとホール',
    u'マリンメッセ福岡',
    u'原宿ビッグトップ',
    u'大阪市中央体育館',
    u'天王洲 銀河劇場',
    u'日本ガイシホール',
    u'神奈川県立音楽堂',
    u'群馬音楽センター',
    u'習志野文化ホール',
    u'神奈川県民ホール 大ホール',
    u'ホクト文化ホール 大ホール (長野県県民文化会館)',
    u'松戸 森のホール21',
    u'オーバード・ホール',
    u'ベイコム総合体育館',
    u'中之島ビッグトップ',
    u'埼玉会館 大ホール',
    u'川崎市教育文化会館',
    u'広島市文化交流会館',
    u'宮崎市民文化ホール 大ホール',
    u'オリックス劇場 (旧 大阪厚生年金会館)',
    u'ハーモニーホール座間',
    u'三重県営サンアリーナ',
    u'仙台サンプラザホール',
    u'住吉スポーツセンター',
    u'埼玉県熊谷会館ホール',
    u'堺市民会館 大ホール',
    u'新国立劇場(中劇場)',
    u'神奈川芸術劇場ホール',
    u'福岡サンパレスホール',
    u'鎌倉芸術館 大ホール',
    u'関内ホール 大ホール',
    u'サンポートホール高松 大ホール',
    u'鹿児島市民文化ホール 第一ホール',
    u'愛知芸術文化センター 愛知県芸術劇場コンサートホール',
    u'オリンパスホール八王子',
    u'グリーンホール相模大野',
    u'サンケイホールブリーゼ',
    u'ザ・シンフォニーホール',
    u'ザ・フェニックスホール',
    u'ホームズスタジアム神戸',
    u'仙台市民会館 大ホール',
    u'千葉市民会館 大ホール',
    u'千葉県文化会館大ホール',
    u'大津市民会館 大ホール',
    u'平塚市民センターホール',
    u'新潟市産業振興センター',
    u'東京ドームシティホール',
    u'福生市民会館 大ホール',
    u'札幌コンサートホール Kitara 大ホール',
    u'さいたまスーパーアリーナ',
    u'サンシティ越谷市民ホール',
    u'サントリーホール大ホール',
    u'パルテノン多摩 大ホール',
    u'佐賀市文化会館 大ホール',
    u'六本木ブルーマンシアター',
    u'大田区民ホール・アプリコ',
    u'新宿文化センター大ホール',
    u'昭和女子大学人見記念講堂',
    u'東京文化会館(大ホール)',
    u'東京文化会館(小ホール)',
    u'柏市民文化会館 大ホール',
    u'秦野市文化会館 大ホール',
    u'よこすか芸術劇場 大ホール',
    u'奈良県文化会館 国際ホール',
    u'幕張メッセ・イベントホール',
    u'豊田市民文化会館 大ホール',
    u'沖縄コンベンションセンター 劇場',
    u'東京国際フォーラム ホールA',
    u'東京国際フォーラム ホールC',
    u'三井住友海上 しらかわホール',
    u'国立代々木競技場 第一体育館',
    u'大宮ソニックシティ 大ホール',
    u'文京シビックホール 大ホール',
    u'武蔵野市民文化会館 大ホール',
    u'盛岡市民文化ホール 大ホール',
    u'神戸国際会館 こくさいホール',
    u'長野県松本文化会館 大ホール',
    u'アクロス福岡シンフォニーホール',
    u'サントリーホール ブルーローズ',
    u'ミューザ川崎シンフォニーホール',
    u'千葉市文化センターアートホール',
    u'川口リリアホール メインホール',
    u'栃木県立日光霧降アイスアリーナ',
    u'石川県立音楽堂コンサートホール',
    u'調布市グリーンホール 大ホール',
    u'滋賀県立芸術劇場 びわ湖ホール 大ホール',
    u'アルファあなぶきホール 大ホール',
    u'グランキューブ大阪 メインホール',
    u'三原市芸術文化センター(ポポロ)',
    u'保谷こもれびホール メインホール',
    u'広島国際会議場フェニックスホール',
    u'府中の森芸術劇場 どりーむホール',
    u'横浜みなとみらいホール 大ホール',
    u'電気文化会館ザ・コンサートホール',
    u'崇城大学市民ホール(熊本市民会館 大ホール)',
    u'すみだトリフォニーホール 大ホール',
    u'日本製紙クリネックススタジアム宮城',
    u'東京オペラシティ コンサートホール',
    u'ウェルシティ広島(広島厚生年金会館)',
    u'栃木県総合文化センター メインホール',
    u'シルク・ドゥ・ソレイユ シアター東京(ZED)',
    u'東京芸術劇場 コンサートホール(大ホール)',
    u'練馬文化センター 大ホール(こぶしホール)',
    u'所沢市民文化センター ミューズ アークホール',
    u'かつしかシンフォニーヒルズ モーツァルトホール',
    ]

organization_names= [
    u'楽天チケット',
    ]

account_pairs = [
    (u'楽天チケット', 2),
    (u'チケットぷあ', 2),
    (u'エフプラス', 2),
    (u'グッドニュース', 1),
    (u'エキゾチックランド', 1),
    (u'楽天野球団', 2),
    (u'東京テレビ事業', 1),
    (u'日本テニス振興会', 1),
    (u'サンセットプロモーション', 1),
    ]

performance_names = [
    u'仙台公演',
    u'東京公演',
    u'名古屋公演',
    u'大阪公演',
    u'福岡公演',
    ]

payment_method_names = [
    u'クレジットカード決済',
    u'楽天あんしん決済',
    u'コンビニ決済 (セブンイレブン)',
    u'窓口支払',
    ]

delivery_method_names = [
    u'郵送',
    u'コンビニ受取 (セブンイレブン)',
    u'窓口受取',
    ]

payment_delivery_method_pair_matrix = [
    [ True, True, True ],
    [ True, True, True ],
    [ False, True, False ],
    [ False, False, True ],
    ]

bank_pairs = [
    (u"0001", u" みずほ銀行"),    
    (u"0005", u" 三菱東京ＵＦＪ銀行"),    
    (u"0009", u" 三井住友銀行"),    
    (u"0010", u" りそな銀行"),    
    (u"0016", u" みずほコーポレート銀行"),    
    (u"0017", u" 埼玉りそな銀行"),    
    (u"0033", u" ジャパンネット銀行"),    
    (u"0034", u" セブン銀行"),
    (u"0035", u" ソニー銀行"),
    (u"0036", u" 楽天銀行"),
    (u"0037", u" 日本振興銀行"),
    (u"0116", u" 北海道銀行"),
    (u"0117", u" 青森銀行"),
    (u"0118", u" みちのく銀行"),
    (u"0119", u" 秋田銀行"),
    (u"0120", u" 北都銀行"),
    (u"0121", u" 荘内銀行"),    
    (u"0122", u" 山形銀行"),    
    (u"0123", u" 岩手銀行"),    
    (u"0124", u" 東北銀行"),    
    (u"0125", u" 七十七銀行"),    
    (u"0126", u" 東邦銀行"),    
    (u"0128", u" 群馬銀行"),    
    (u"0129", u" 足利銀行"),    
    (u"0130", u" 常陽銀行"),    
    (u"0131", u" 関東つくば銀行"),    
    (u"0133", u" 武蔵野銀行"),    
    (u"0134", u" 千葉銀行"),    
    (u"0135", u" 千葉興業銀行"),    
    (u"0137", u" 東京都民銀行"),    
    (u"0138", u" 横浜銀行"),    
    (u"0140", u" 第四銀行"),    
    (u"0141", u" 北越銀行"),    
    (u"0142", u" 山梨中央銀行"),    
    (u"0143", u" 八十二銀行"),    
    (u"0144", u" 北陸銀行"),    
    (u"0145", u" 富山銀行"),    
    (u"0146", u" 北國銀行"),    
    (u"0147", u" 福井銀行"),    
    (u"0149", u" 静岡銀行"),    
    (u"0150", u" スルガ銀行"),    
    (u"0151", u" 清水銀行"),    
    (u"0152", u" 大垣共立銀行"),    
    (u"0153", u" 十六銀行"),    
    (u"0154", u" 三重銀行"),    
    (u"0155", u" 百五銀行"),    
    (u"0157", u" 滋賀銀行"),    
    (u"0158", u" 京都銀行"),    
    (u"0159", u" 近畿大阪銀行"),    
    (u"0160", u" 泉州銀行"),    
    (u"0161", u" 池田銀行"),    
    (u"0162", u" 南都銀行"),    
    (u"0163", u" 紀陽銀行"),    
    (u"0164", u" 但馬銀行"),    
    (u"0166", u" 鳥取銀行"),    
    (u"0167", u" 山陰合同銀行"),    
    (u"0168", u" 中国銀行"),    
    (u"0169", u" 広島銀行"),    
    (u"0170", u" 山口銀行"),    
    (u"0172", u" 阿波銀行"),    
    (u"0173", u" 百十四銀行"),    
    (u"0174", u" 伊予銀行"),    
    (u"0175", u" 四国銀行"),    
    (u"0177", u" 福岡銀行"),    
    (u"0178", u" 筑邦銀行"),    
    (u"0179", u" 佐賀銀行"),    
    (u"0180", u" 十八銀行"),    
    (u"0181", u" 親和銀行"),    
    (u"0182", u" 肥後銀行"),    
    (u"0183", u" 大分銀行"),
    (u"0184", u" 宮崎銀行"),
    (u"0185", u" 鹿児島銀行"),    
    (u"0187", u" 琉球銀行"),    
    (u"0188", u" 沖縄銀行"),    
    (u"0190", u" 西日本シティ銀行"),    
    (u"0401", u" シティバンク銀行"),    
    (u"0502", u" 札幌銀行"),    
    (u"0508", u" きらやか銀行"),    
    (u"0509", u" 北日本銀行"),    
    (u"0512", u" 仙台銀行"),    
    (u"0513", u" 福島銀行"),    
    (u"0514", u" 大東銀行"),    
    (u"0516", u" 東和銀行"),    
    (u"0517", u" 栃木銀行"),    
    (u"0519", u" 茨城銀行"),    
    (u"0522", u" 京葉銀行"),    
    (u"0525", u" 東日本銀行"),    
    (u"0526", u" 東京スター銀行"),    
    (u"0530", u" 神奈川銀行"),    
    (u"0532", u" 大光銀行"),    
    (u"0533", u" 長野銀行"),    
    (u"0534", u" 富山第一銀行"),    
    (u"0537", u" 福邦銀行"),    
    (u"0538", u" 静岡中央銀行"),    
    (u"0541", u" 岐阜銀行"),    
    (u"0542", u" 愛知銀行"),    
    (u"0543", u" 名古屋銀行"),    
    (u"0544", u" 中京銀行"),    
    (u"0546", u" 第三銀行"),    
    (u"0547", u" びわこ銀行"),    
    (u"0554", u" 関西アーバン銀行"),    
    (u"0555", u" 大正銀行"),    
    (u"0562", u" みなと銀行"),    
    (u"0565", u" 島根銀行"),    
    (u"0566", u" トマト銀行"),    
    (u"0569", u" もみじ銀行"),    
    (u"0570", u" 西京銀行"),    
    (u"0572", u" 徳島銀行"),    
    (u"0573", u" 香川銀行"),    
    (u"0576", u" 愛媛銀行"),    
    (u"0578", u" 高知銀行"),    
    (u"0582", u" 福岡中央銀行"),    
    (u"0583", u" 佐賀共栄銀行"),    
    (u"0585", u" 長崎銀行"),    
    (u"0587", u" 熊本ファミリー銀行"),    
    (u"0590", u" 豊和銀行"),    
    (u"0591", u" 宮崎太陽銀行"),    
    (u"0594", u" 南日本銀行"),    
    (u"0596", u" 沖縄海邦銀行"),    
    (u"0597", u" 八千代銀行"),
    ]

role_seeds = {
    u'administrator': [
        (u'administrator', 1),
        (u'asset_editor', 1),
        (u'event_viewer', 1),
        (u'event_editor', 1),
        (u'topic_viewer', 1),
        (u'ticket_editor', 1),
        (u'magazine_viewer', 1),
        (u'magazine_editor', 1),
        (u'asset_viewer', 1),
        (u'asset_editor', 1),
        (u'page_viewer', 1),
        (u'page_editor', 1),
        (u'tag_editor', 1),
        (u'layout_viewer', 1),
        (u'layout_editor', 1),
        ],
    u'superuser': [
        (u'event_viewer', 1),
        (u'event_editor', 1),
        (u'topic_viewer', 1),
        (u'ticket_editor', 1),
        (u'magazine_viewer', 1),
        (u'magazine_editor', 1),
        (u'asset_viewer', 1),
        (u'asset_editor', 1),
        (u'page_viewer', 1),
        (u'page_editor', 1),
        (u'tag_editor', 1),
        (u'layout_viewer', 1),
        (u'layout_editor', 1),
        ],
    }

operator_seeds = {
    u'Administrator': [ u'administrator' ],
    u'オペレータ': [ u'superuser' ],
    }

class Data(_Data):
    def __init__(self, schema, **fields):
        _Data.__init__(self, schema, auto('id'), **fields)

def random_date():
    return datetime.now().date().replace(month=1, day=1) + relativedelta(days=randint(0, 364))

def build_site_datum(name):
    colgroup_seat_schema_pair = [('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i], _name) for i, (_name, type) in enumerate(stock_type_pairs) if type == 0]
    return Data(
        'Site',
        name=name,
        _config=dict(
            colgroups=[
                (colgroup, u'colgroup-%s' % colgroup, [u'%s-%d' % (colgroup, i + 1) for i in range(0, randint(1, 50) * 10)]) \
                for colgroup, seat_schema in colgroup_seat_schema_pair
                ],
            seats_per_row=10
            )
        )

sites = [build_site_datum(name) for name in site_names]

banks = [
    Data(
        'Bank',
        code=code,
        name=name
        ) \
    for code, name in bank_pairs
    ]

payment_method_plugin_data = [
    Data(
        'PaymentMethodPlugin',
        name=name
        ) \
    for name in payment_method_names
    ]

delivery_method_plugin_data = [
    Data(
        'DeliveryMethodPlugin',
        name=name
        ) \
    for name in delivery_method_names
    ]

operator_role_map = dict(
    (
        name,
        Data(
            'OperatorRole',
            name=name,
            permissions=rel(
                [Data(
                    'Permission',
                    category_name=category_name,
                    permit=permit
                    ) \
                for category_name, permit in permissions
                ],
                'operator_role_id'
                ),
            status=1
            )
        ) \
    for name, permissions in role_seeds.iteritems()
    )

def build_payment_method_datum(organization, payment_method_plugin):
    return Data(
        'PaymentMethod',
        name=payment_method_plugin.name,
        fee=randint(1, 4) * 100,
        organization_id=organization,
        payment_plugin_id=payment_method_plugin
        )

def build_delivery_method_datum(organization, delivery_method_plugin):
    return Data(
        'DeliveryMethod',
        name=delivery_method_plugin.name,
        fee=randint(1, 4) * 100,
        organization_id=organization,
        delivery_plugin_id=delivery_method_plugin
        )

def build_account_datum(name, type):
    return Data(
        'Account',
        name=name,
        account_type=type,
        user_id=build_user_datum()
        )

def build_seat_datum(group_l0_id, l0_id, stock):
    return Data(
        'Seat',
        l0_id=l0_id,
        stock_id=stock,
        stock_type_id=stock.stock_type_id,
        venue_id=None,
        group_l0_id=group_l0_id,
        venue_areas=rel(
            [],
            ('venue_id', 'group_l0_id'),
            'venue_area_id',
            'VenueArea_group_l0_id'
            ),
        status=rel(
            [_Data(
                'SeatStatus',
                'seat_id',
                status=1
                )],
            'seat_id'
            )
        )

def build_venue_area_datum(venue, colgroup):
    return Data(
        'VenueArea',
        name=colgroup[0],
        groups=rel(
            [_Data(
                'VenueArea_group_l0_id',
                (),
                venue_id=venue,
                group_l0_id=colgroup[1]
                )],
            'venue_area_id'
            )
        )

def build_adjacency_set_datum(l0_id_to_seat, config, n):
    seats_per_row = config['seats_per_row']
    adjacency_data = []
    for colgroup_name, colgroup_id, seat_ids in config['colgroups']:
        for row_num in range(0, len(seat_ids), seats_per_row):
            seats_in_row = [
                l0_id_to_seat[l0_id] \
                for l0_id in seat_ids[row_num:row_num + seats_per_row]
                ]
            for i in range(0, seats_per_row - n + 1):
                adjacency_data.append(Data(
                    'SeatAdjacency',
                    seats=rel(
                        seats_in_row[i:i+n],
                        'seat_adjacency_id',
                        'seat_id',
                        'Seat_SeatAdjacency',
                        )
                    ))
    return Data(
        'SeatAdjacencySet',
        seat_count=n,
        adjacencies=rel(
            adjacency_data,
            'adjacency_set_id'
            )
        )

def build_venue_datum(organization, site, stock_sets):
    logger.info(u"Building Venue %s" % site.name)
    config = site._config
    seats = []
    l0_id_to_seat = {}
    for i, stocks in stock_sets:
        colgroup = config['colgroups'][i]
        seat_index = 0
        for stock in stocks:
            for l0_id in colgroup[2][seat_index:seat_index + stock.quantity]:
                seat_datum = build_seat_datum(colgroup[1], l0_id, stock)
                seats.append(seat_datum)
                l0_id_to_seat[l0_id] = seat_datum
            seat_index += stock.quantity

    adjacency_set_data = [
        build_adjacency_set_datum(l0_id_to_seat, config, n) \
        for n in range(2, config['seats_per_row'])
        ]

    retval = Data(
        'Venue',
        name=site.name,
        seats=rel(
            seats,
            'venue_id'
            ),
        site_id=site,
        organization_id=organization,
        adjacency_sets=rel(
            adjacency_set_data,
            'venue_id'
            )
        )
    retval.areas = rel(
        [
            build_venue_area_datum(retval, config['colgroups'][i]) \
            for i, _ in stock_sets
            ],
            ()
        )
    return retval

def build_bank_account_datum():
    return Data(
        'BankAccount',
        bank_id=choice(banks),
        account_type=1,
        account_number=u''.join(choice(u'0123456789') for _ in range(0, 7)),
        account_owner=u'ラクテン タロウ'
        )

def build_user_datum():
    return Data(
        'User',
        bank_account_id=build_bank_account_datum(),
        user_profile=rel(
            [_Data(
                'UserProfile',
                'user_id',
                email=lambda self: "dev+test%03d@ticketstar.jp" % self._id[0],
                nick_name=lambda self: "dev+test%03d@ticketstar.jp" % self._id[0],
                first_name=lambda self: u"太郎%d" % self._id[0],
                last_name=u"楽天",
                first_name_kana=u"タロウ",
                last_name_kana=u"ラクテン",
                birth_day=date(randint(1930, 2000), randint(1, 12), 1) + relativedelta(days=randint(0, 30)),
                sex=1,
                zip="251-0036",
                prefecture=u"東京都",
                city=u"品川区",
                street=u"",
                address=u"東五反田5-21-15'",
                other_address=u"メタリオンOSビル",
                tel_1=u"03-9999-9999",
                tel_2=u"090-0000-0000",
                fax=u"03-9876-5432"
                )],
            'user_id'
            )
        )

def build_operator_datum(name, operator_roles):
    return Data(
        'Operator',
        name=name,
        email=lambda self: 'dev+test%03d@ticketstar.jp' % self._id[0],
        roles=rel(
            operator_roles,
            'operator_id',
            'operator_role_id',
            'OperatorRole_Operator'
            ),
        expire_at=None,
        status=1,
        auth=rel([
            _Data(
                'OperatorAuth',
                'operator_id',
                login_id=lambda self: u'dev+test%03d@ticketstar.jp' % self._id[0] if self._id[0] > 1 else u'admin',
                password=hashlib.md5('admin').hexdigest(),
                auth_code=u'auth_code',
                access_token=u'access_token',
                secret_key=u'secret_key'
                )],
            'operator_id'
            )
        )

def gendigest(password):
    return hashlib.sha1(SALT + password).hexdigest()

def build_user_credential(user):
    return Data(
        'UserCredential',
        auth_identifier=user.email,
        auth_secret=gendigest("asdfasdf")
        )

def build_organization_datum(name):
    logger.info(u"Building Organization %s" % name)
    retval = Data(
        'Organization',
        name=name,
        events=None,
        accounts=rel(
            [build_account_datum(name, type) for name, type in account_pairs],
            'organization_id'
            ),
        operators=rel(
            [
                build_operator_datum(
                    operator_name,
                    [operator_role_map[role_name] \
                     for role_name in role_names]
                    ) \
                for operator_name, role_names in operator_seeds.iteritems()
                ],
            'organization_id',
            )
        )
    payment_method_data = [
        build_payment_method_datum(
            retval,
            payment_method_plugin_datum) \
        for payment_method_plugin_datum in payment_method_plugin_data
        ]
    delivery_method_data = [
        build_delivery_method_datum(
            retval,
            delivery_method_plugin_datum) \
        for delivery_method_plugin_datum in delivery_method_plugin_data
        ]
    retval.payment_methods = rel(
        payment_method_data,
        'organization_id'
        )
    retval.delivery_methods = rel(
        delivery_method_data,
        'organization_id'
        )
    event_data = [
        build_event_datum(retval, name) \
        for name in event_names[0:20]
        ]
    retval.events = rel(
        event_data,
        'organization_id'
        )
    return retval

def build_sales_segment_datum(organization, name, start_at, end_at):
    payment_delivery_method_pairs = [
        Data(
            'PaymentDeliveryMethodPair',
            transaction_fee=randint(1, 4) * 100,
            delivery_fee=randint(1, 4) * 100,
            discount=randint(0, 40) * 10,
            discount_unit=randint(0, 1),
            payment_method_id=organization.payment_methods[payment_method_index],
            delivery_method_id=organization.delivery_methods[delivery_method_index],
            ) \
        for payment_method_index, row in enumerate(payment_delivery_method_pair_matrix) \
        for delivery_method_index, enabled in enumerate(row) if enabled
        ]

    return Data(
        'SalesSegment',
        name=name,
        start_at=start_at,
        end_at=end_at,
        upper_limit=randint(1, 10),
        seat_choice=randint(0, 1) != 0,
        payment_delivery_method_pairs=rel(
            payment_delivery_method_pairs,
            'sales_segment_id'
            )
        )

def build_stock_allocation_datum(stock_type, quantity):
    return Data(
        'StockAllocation',
        stock_type_id=stock_type,
        quantity=quantity,
        )

def build_stock_datum(stock_type, stock_holder, quantity):
    return Data(
        'Stock',
        stock_type_id=stock_type,
        quantity=quantity,
        stock_holder_id=stock_holder,
        stock_status=rel(
            [_Data(
                'StockStatus',
                'stock_id',
                quantity=quantity,
                )],
            'stock_id'
            )
        )

def build_performance_datum(organization, event, name, performance_date):
    logger.info(u"Building Performance %s" % name)

    site = choice(sites)
    site_config = site._config
    stock_allocation_data = []
    stock_data = []
    stock_sets = []
    colgroup_index = 0
    for stock_type in event.stock_types:
        stock_set = []
        if stock_type.type == 0:
            colgroup = site_config['colgroups'][colgroup_index]
            quantity = len(colgroup[2])
            stock_sets.append((colgroup_index, stock_set))
            colgroup_index += 1
        else:
            quantity = randint(10, 100) * 10
        stock_allocation_datum = build_stock_allocation_datum(stock_type, quantity)
        rest = quantity
        for i, stock_holder in enumerate(event.stock_holders):
            assigned = rest if i == len(event.stock_holders) - 1 else randint(0, rest)
            stock_datum = build_stock_datum(stock_type, stock_holder, assigned)
            stock_data.append(stock_datum)
            stock_set.append(stock_datum)
            rest -= assigned
    
    venue = build_venue_datum(organization, site, stock_sets)

    retval = Data(
        'Performance',
        name=name,
        open_on=datetime.combine(performance_date, time(18, 0, 0)),
        start_on=datetime.combine(performance_date, time(19, 0, 0)),
        end_on=datetime.combine(performance_date, time(21, 0, 0)),
        stock_allocations=rel(
            stock_allocation_data,
            'performance_id'
            ),
        stocks=rel(
            stock_data,
            'performance_id'
            ),
        venue=rel(
            [venue],
            'performance_id'
            )
        )
    retval.product_items = rel(
        list(chain(*(
            build_product_item_data(retval, product, stock_data) \
            for product in event.products
            ))),
        'performance_id'
        )
    return retval

def build_stock_type_datum(name, type):
    return Data(
        'StockType',
        name=name,
        type=type,
        style=u'{}'
        )

def build_product_item(performance, product, stock, price, quantity):
    return Data(
        'ProductItem',
        item_type=1,
        price=price,
        stock_id=stock,
        performance_id=performance,
        quantity=quantity
        )

def build_product_item_data(performance, product, stocks):
    def find_stock(stock_type_name):
        for stock in stocks:
            if stock.stock_type_id.name == stock_type_name:
                return stock
        raise Exception("No such stock that corresponds to %s" % stock_type_name)

    product_item_seeds = stock_type_combinations[product.name]
    return [
        build_product_item(
            performance, product,
            find_stock(stock_type_name), price, 1)
            for stock_type_name, price in product_item_seeds
        ]

def build_product_data(sales_segment):
    return [
        Data(
            'Product',
            name=name,
            price=sum(price for stock_type_name, price in product_item_seeds),
            sales_segment_id=sales_segment,
            ) \
        for name, product_item_seeds in stock_type_combinations.iteritems()
        ]

def build_event_datum(organization, title):
    logger.info(u"Building Event %s" % title)
    event_date = random_date()
    stock_type_data = [build_stock_type_datum(_name, type) for _name, type in stock_type_pairs]
    sales_segment_data = [
        build_sales_segment_datum(
            organization,
            u'先行',
            datetime.combine(event_date, time(10, 0)) - relativedelta(months=-3),
            datetime.combine(event_date, time(0, 0)) - relativedelta(months=-2, seconds=-1)
            ),
        build_sales_segment_datum(
            organization,
            u'一般',
            datetime.combine(event_date, time(10, 0)) - relativedelta(months=2),
            datetime.combine(event_date, time(0, 0)) - relativedelta(seconds=-1)
            )
        ]
    stock_holder_data = [
        Data(
            'StockHolder',
            name=account.name,
            account_id=account,
            style=u'{}'
            ) \
        for account in organization.accounts
        ]
    retval = Data(
        'Event',
        title=title,
        organization_id=organization,
        stock_types=rel(
            stock_type_data,
            'event_id'
            ),
        account_id=choice(organization.accounts),
        sales_segments=rel(
            sales_segment_data,
            'event_id'
            ),
        stock_holders=rel(
            stock_holder_data,
            'event_id'
            ),
        products=rel(
            list(chain(*(
                build_product_data(sales_segment_datum) \
                for sales_segment_datum in sales_segment_data
                ))),
            'event_id'
            )
        )
    retval.performances = rel(
        [
            build_performance_datum(
                organization, retval, name,
                event_date + relativedelta(days=i)) \
            for i, name in enumerate(performance_names)],
        'event_id'
        )
    return retval

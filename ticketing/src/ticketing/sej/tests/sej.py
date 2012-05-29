# -*- coding:utf-8 -*-
import unittest
#from ..payment import SejInstantPaymentFileParser
from ticketing.sej.payment import SejPayment, SejPaymentType, SejTicketType, request_order
import datetime
import cgi
import BaseHTTPServer,CGIHTTPServer
from ticketing.utils import JavaHashMap

class SejTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def _test_request_file_get(self):

        '''
        https://inticket.sej.co.jp/order/getfile.do
        '''

        payment = SejPayment(url = u'https://pay.r1test.com/order/getfile.do', secret_key = u'E6PuZ7Vhe7nWraFW')
        params = JavaHashMap()
        # ショップID
        params['X_shop_id']  = u'30520'
        params['X_tuchi_kbn'] = u'01'
        params['X_date'] = u'20120527'

        # 連絡先2
        payment.request(params, 0)

    def _test_request_order_cancel(self):
        payment = SejPayment(url = u'https://pay.r1test.com/order/cancelorder.do', secret_key = u'E6PuZ7Vhe7nWraFW')
        params = JavaHashMap()
        # ショップID
        params['X_shop_id']         = u'30520'
        # ショップ名称
        params['X_shop_order_id']   = u'orderid00001'
        # 連絡先1
        params['X_haraikomi_no']    = u'2347462348670'
        #params['X_hikikae_no']      = u'contact'
        # 連絡先2
        payment.request(params, 0)

        # 該当が無い場合
        # <SENBDATA>Error_Type=21&Error_Msg=Not Found&Error_Field=X_shop_order_id&</SENBDATA><SENBDATA>DATA=END</SENBDATA>


    def test_request_order(self):
        '''
            決済要求 https://inticket.sej.co.jp/order/order.do
        '''
        sejTicketOrder = request_order(
            shop_name       = u'楽天チケット',
            contact_01      = u'contact',
            contact_02      = u'連絡先2',
            order_id        = u"orderid00001",
            username        = u"お客様氏名",
            username_kana   = u'コイズミモリヨシ',
            tel             = u'0312341234',
            zip             = u'1070062',
            email           = u'dev@ticketstar.jp',
            total           = 15000,
            ticket_total    = 13000,
            commission_fee  = 1000,
            ticketing_fee   = 1000,

            payment_type    = SejPaymentType.CashOnDelivery,
            payment_due_datetime = datetime.datetime(2012,3,30,7,00), #u'201207300700',
            ticketing_sub_due_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',

            tickets = [
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<?xml version="1.0" encoding="Shift_JIS" ?>
                    <TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                )
            ]
        )

        print sejTicketOrder

'''
    def test_sej_update(self):
        gw = JavaGateway()
        jString = gw.jvm.java.lang.String
        ##---------------------------------------------
        ## １．ＳＥＪ決済クライアントモジュール生成
        ##---------------------------------------------

        ## モジュールを生成する
        sejPayment = gw.jvm.jp.co.sej.od.util.SejPayment()
  
        ##---------------------------------------------
        ## ２．内部変数初期化
        ##---------------------------------------------
        ## 初期化する
        sejPayment.Clear()
  
        ##---------------------------------------------
        ## ３．プロパティ設定
        ##---------------------------------------------
        ## IN決済要求送信用URLを設定
        sejPayment.SetURL(u"https:##myurl/order/updateorder.do")
        ## 秘密キーを設定
        sejPayment.SetSecretKey(u"9999999999999999")
        ## ショップ様HTTPプロキシサーバを設定
        sejPayment.SetProxyServerHost(u"myproxy")
        sejPayment.SetProxyServerPort(7777)
        ## ショップ様HTTPプロキシサーバの認証キーを設定
        sejPayment.SetProxyAuth(u"myid:mypassword")
        ## 回線接続タイムアウトを設定
        sejPayment.SetTimeOut(120)
        ## 回線接続リトライ回数を設定
        sejPayment.SetRetryCount(3)
        ## 回線接続リトライ間隔を設定
        sejPayment.SetRetryInterval(5)
  
        ##---------------------------------------------
        ## ４．送信値設定
        ##---------------------------------------------
        ## 更新理由を設定(例:01[項目変更])
        sejPayment.Addinput(u"X_upd_riyu", u"01")
        ## ショップIDを設定
        sejPayment.Addinput(u"X_shop_id", u"myshopid")
        ## 注文IDを設定
        sejPayment.Addinput(u"X_shop_order_id", u"orderid00001")
        ## 合計金額を設定(例:\20,000)
        sejPayment.Addinput(u"X_goukei_kingaku", u"020000")
        ## 支払期限日時を設定(例:2010年2月28日15時)
        sejPayment.Addinput(u"X_pay_lmt", u"201002281500")
        ## チケット代金を設定(例:\15,000)
        sejPayment.Addinput(u"X_ticket_daikin", u"015000")
        ## チケット購入代金を設定(例:\3,000)
        sejPayment.Addinput(u"X_ticket_kounyu_daikin", u"003000")
        ## 発券代金を設定(例:\2,000)
        sejPayment.Addinput(u"X_hakken_daikin", u"002000")
        ## チケット枚数を設定
        sejPayment.Addinput(u"X_ticket_cnt", u"01")
        ## 本券購入枚数を設定
        sejPayment.Addinput(u"X_ticket_hon_cnt", u"01")
        ## チケット区分を設定(例:1[本券（チケットバーコード有り）])
        sejPayment.Addinput(u"X_ticket_kbn_01", u"1")
        ## 興行名を設定
        sejPayment.Addinput(u"kougyo_mei_01", u"興行名称")
        ## 公演名を設定
        sejPayment.Addinput(u"kouen_mei_01", u"公演名")
        ## 公演日時を設定(例:2010年3月2日 17時30分)
        sejPayment.Addinput(u"X_kouen_date_01", u"201003021730")
        ## テンプレートコードを設定
        sejPayment.Addinput(u"X_ticket_template_01", u"mytemplate")
        ## 券面情報を設定
        sejPayment.Addinput(u"ticket_text_01", u"<?xml version='1.0' encoding='Shift_JIS' ?><TICKET><MR01>…")
  
        ##---------------------------------------------
        ## ５．注文情報更新要求送信
        ##---------------------------------------------
        ## 注文情報更新要求
        iRet = sejPayment.Request(False)
        ## 結果出力
        print u"送信要求結果   ：" + jString.valueOf(iRet)
        print u"------------------------------------------"
        ## エラー処理
        if iRet != 0:
            ## エラー内容を取得
            sErrorMsg = sejPayment.GetErrorMsg() 
            ## エラー内容出力
            print u"エラー内容     ：" + sErrorMsg
            ## 終了する

        self.assertEquals(iRet, 0)
  
        ##---------------------------------------------
        ## ６．戻り値取得
        ##---------------------------------------------
        ## 注文IDを取得
        sOrderId = sejPayment.GetOutput(u"X_shop_order_id")
        ## 払込票番号を取得
        sHaraikomiNo = sejPayment.GetOutput(u"X_haraikomi_no")
        ## URL情報を取得
        sUrlInfo = sejPayment.GetOutput(u"X_url_info")
        ## 依頼票IDを取得
        sIraihyoId = sejPayment.GetOutput(u"iraihyo_id_00")
        ## チケット枚数を取得
        sTicketCnt = sejPayment.GetOutput(u"X_ticket_cnt")
        ## 本券購入枚数を取得                        
        sTicketHonCnt = sejPayment.GetOutput(u"X_ticket_hon_cnt")
        ## チケットバーコード番号を取得
        sTicketBarCode = sejPayment.GetOutput(u"X_barcode_no_01")
  
        ## 戻り値出力
        print u"注文ID　　：" + sOrderId
        print u"払込票番号：" + sHaraikomiNo
        print u"払込票ID  ：" + sIraihyoId


    def test_sej_cancel(self):
        gw = JavaGateway()
        jString = gw.jvm.java.lang.String
        ##---------------------------------------------
        ## １．ＳＥＪ決済クライアントモジュール生成
        ##---------------------------------------------
        
        ## モジュールを生成する
        sejPayment = gw.jvm.jp.co.sej.od.util.SejPayment()
  
        ##---------------------------------------------
        ## ２．内部変数初期化
        ##---------------------------------------------
        ## 初期化する
        sejPayment.Clear()
  
        ##---------------------------------------------
        ## ３．プロパティ設定
        ##---------------------------------------------
        ## INチケットキャンセル要求送信用URLを設定
        sejPayment.SetURL(u"https:##myurl/od/cancel.asp")
        ## 秘密キーを設定
        sejPayment.SetSecretKey(u"9999999999999999")
        ## ショップ様HTTPプロキシサーバを設定
        sejPayment.SetProxyServerHost(u"myproxy")
        sejPayment.SetProxyServerPort(7777)
        ## ショップ様HTTPプロキシサーバの認証キーを設定
        sejPayment.SetProxyAuth(u"myid:mypassword")
        ## 回線接続タイムアウトを設定
        sejPayment.SetTimeOut(120)
        ## 回線接続リトライ回数を設定
        sejPayment.SetRetryCount(3)
        ## 回線接続リトライ間隔を設定
        sejPayment.SetRetryInterval(5)
  
        ##---------------------------------------------
        ## ４．送信値設定
        ##---------------------------------------------
        ## ショップIDを設定
        sejPayment.Addinput(u"X_shop_id", u"myshopid")
        ## 注文IDを設定
        sejPayment.Addinput(u"X_shop_order_id", u"orderid00001")
  
        ##---------------------------------------------
        ## ５．キャンセル要求送信
        ##---------------------------------------------
        ## キャンセル要求
        iRet = sejPayment.Cancel()
        ## 結果出力
        print u"送信要求結果   ：" + jString.valueOf(iRet)
        print u"------------------------------------------"
        ## エラー処理
        if iRet != 0:
            ## エラー内容を取得
            sErrorMsg = sejPayment.GetErrorMsg()
            ## エラー内容出力
            print u"エラー内容     ：" + sErrorMsg
            ## 終了する

        self.assertEquals(iRet, 0)
'''
if __name__ == u"__main__":
    unittest.main()
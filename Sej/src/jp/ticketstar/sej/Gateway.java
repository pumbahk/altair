package jp.ticketstar.sej;

//import py4j.GatewayServer;

import jp.co.sej.od.util.SejPayment;
import jp.co.sej.od.util.SejPaymentInterface;

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 4/19/12
 * Time: 9:36 PM
 * To change this template use File | Settings | File Templates.
 */
public class Gateway {

    //public static void main(String[] args) {
        //GatewayServer server = new GatewayServer(new Gateway());
        //server.start();
        //System.out.println("Gateway Server Started");

    //}

    public static void main(String[] args) throws Exception {

   		//---------------------------------------------
   		// １．ＳＥＪ決済クライアントモジュール生成
   		//---------------------------------------------
   		// モジュールを生成する
   		SejPaymentInterface sejPayment = new SejPayment();

   		//---------------------------------------------
   		// ２．内部変数初期化
   		//---------------------------------------------
   		// 初期化する
   		sejPayment.Clear();

   		//---------------------------------------------
   		// ３．プロパティ設定
   		//---------------------------------------------
   		// INチケット決済要求送信用URLを設定
   	    // sejPayment.SetURL("http://sv2.ticketstar.jp/test.php");
   	    sejPayment.SetURL("https://pay.r1test.com/order/order.do");
   		// 秘密キーを設定
   		sejPayment.SetSecretKey("E6PuZ7Vhe7nWraFW");
   		// ショップ様HTTPプロキシサーバを設定
   		// sejPayment.SetProxyServerHost("myproxy");
   		// sejPayment.SetProxyServerPort(7777);
   		// ショップ様HTTPプロキシサーバの認証キーを設定
   		// sejPayment.SetProxyAuth("myid:mypassword");
   		// 回線接続タイムアウトを設定
   		sejPayment.SetTimeOut(120);
   		// 回線接続リトライ回数を設定
   		sejPayment.SetRetryCount(3);
   		// 回線接続リトライ間隔を設定
   		sejPayment.SetRetryInterval(5);

        
  
        // ショップID
        sejPayment.Addinput("X_shop_id", "30520");
        // ショップ名称
        sejPayment.Addinput("shop_namek", "楽天チケット");
        // 連絡先1
        sejPayment.Addinput("X_renraku_saki", "contact");
        // 連絡先2
        sejPayment.Addinput("renraku_saki", "連絡先2");
        // 注文ID
        sejPayment.Addinput("X_shop_order_id", "orderid00001");
        // お客様氏名
        sejPayment.Addinput("user_namek", "お客様氏名");
        // お客様氏名カナ
        sejPayment.Addinput("user_name_kana", "コイズミモリヨシ");
        // お客様電話番号
        sejPayment.Addinput("X_user_tel_no", "0312341234");
        //　お客様郵便番号
        sejPayment.Addinput("X_user_post", "1070062");
        // お客様メールアドレス
        sejPayment.Addinput("X_user_email", "dev@ticketstar.jp");
        // 処理区分
        sejPayment.Addinput("X_shori_kbn", "01");
        // 合計金額 = チケット代金 + チケット購入代金+発券代金の場合
        sejPayment.Addinput("X_goukei_kingaku", "015000");
        // 支払期限日時 YYYYMMDDhhmm。店舗での支払有効期限。
        sejPayment.Addinput("X_pay_lmt", "201207010700");
        // チケット代金
        sejPayment.Addinput("X_ticket_daikin", "010000");
        // チケット購入代金
        sejPayment.Addinput("X_ticket_kounyu_daikin", "004000");
        // 発券開始日時
        sejPayment.Addinput("X_hakken_mise_date", "201207010800");
        // 発券開始日時
        //params['X_hakken_mise_date_sts'] = ''
        // 発券期限日時
        sejPayment.Addinput("X_hakken_lmt", "201207310700");
        // 発券期限日時状態フラグ
        //params['X_hakken_lmt_sts']  = ''
        //
        sejPayment.Addinput("X_saifuban_hakken_lmt", "201207010800");
        sejPayment.Addinput("X_hakken_daikin", "001000");
        sejPayment.Addinput("X_ticket_cnt", "03");
        sejPayment.Addinput("X_ticket_hon_cnt", "01");

        sejPayment.Addinput("X_ticket_kbn_01", "2");
        sejPayment.Addinput("kougyo_mei_01", "テスト興行");
        sejPayment.Addinput("kouen_mei_01", "テスト公演");
        sejPayment.Addinput("X_kouen_date_01", "201207310800");
        sejPayment.Addinput("X_ticket_template_01", "");
        sejPayment.Addinput("ticket_text_01", "<?xml version=\"1.0\" encoding=\"Shift_JIS\" ?>" +
"<TICKET>"+
"  <TEST1>test&//x20;test</TEST1>"+
"  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>"+
"  <TEST3>&//x3000;</TEST3>"+
"  <FIXTAG01></FIXTAG01>"+
"  <FIXTAG02></FIXTAG02>"+
"  <FIXTAG03></FIXTAG03>"+
"  <FIXTAG04></FIXTAG04>"+
"  <FIXTAG05></FIXTAG05>"+
"  <FIXTAG06></FIXTAG06>"+
"</TICKET>");

        sejPayment.Addinput("X_ticket_kbn_02", "4");
        sejPayment.Addinput("kougyo_mei_02", "テスト興行");
        sejPayment.Addinput("kouen_mei_02", "テスト公演");
        sejPayment.Addinput("X_kouen_date_02", "201207310800");
        sejPayment.Addinput("X_ticket_template_02", "");
        sejPayment.Addinput("ticket_text_02", "<?xml version=\"1.0\" encoding=\"Shift_JIS\" ?>" +
"<TICKET>"+
"  <TEST1>test&//x20;test</TEST1>"+
"  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>"+
"  <TEST3>&//x3000;</TEST3>"+
"  <FIXTAG01></FIXTAG01>"+
"  <FIXTAG02></FIXTAG02>"+
"  <FIXTAG03></FIXTAG03>"+
"  <FIXTAG04></FIXTAG04>"+
"  <FIXTAG05></FIXTAG05>"+
"  <FIXTAG06></FIXTAG06>"+
"</TICKET>");

        sejPayment.Addinput("X_ticket_kbn_03", "4");
        sejPayment.Addinput("kougyo_mei_03", "テスト興行");
        sejPayment.Addinput("kouen_mei_03", "テスト公演");
        sejPayment.Addinput("X_kouen_date_03", "201207310800");
        sejPayment.Addinput("X_ticket_template_03", "");
        sejPayment.Addinput("ticket_text_03", "チケット");
        sejPayment.Addinput("ticket_text_02", "<?xml version=\"1.0\" encoding=\"Shift_JIS\" ?>" +
"<TICKET>"+
"  <TEST1>test&//x20;test</TEST1>"+
"  <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>"+
"  <TEST3>&//x3000;</TEST3>"+
"  <FIXTAG01></FIXTAG01>"+
"  <FIXTAG02></FIXTAG02>"+
"  <FIXTAG03></FIXTAG03>"+
"  <FIXTAG04></FIXTAG04>"+
"  <FIXTAG05></FIXTAG05>"+
"  <FIXTAG06></FIXTAG06>"+
"</TICKET>");

   		//---------------------------------------------
   		// ５．決済要求送信
   		//---------------------------------------------
   		// 決済要求
   		int iRet = sejPayment.Request(false);
   		// 結果出力
   		System.out.println("送信要求結果   ：" + String.valueOf(iRet));
   		System.out.println("------------------------------------------");
   		// エラー処理
   		if(iRet != 0) {
   			// エラー内容を取得
   			String sErrorMsg = sejPayment.GetErrorMsg();
   			// エラー内容出力
   			System.out.println("エラー内容     ：" + sErrorMsg);
   			// 終了する
   			return;
   		}

   		//---------------------------------------------
   		// ６．戻り値取得
   		//---------------------------------------------
   		// 注文IDを取得
   		String sOrderId = sejPayment.GetOutput("X_shop_order_id");
   		// 払込票番号を取得
   		String sHaraikomiNo = sejPayment.GetOutput("X_haraikomi_no");
   		// URL情報を取得
   		String sUrlInfo = sejPayment.GetOutput("X_url_info");
   		// 依頼表番号を取得
   		String sIraihyoId = sejPayment.GetOutput("iraihyo_id_00");
   		// チケット枚数を取得
   		String sTicketCnt = sejPayment.GetOutput("X_ticket_cnt");
   		// 本券購入枚数を取得
   		String sTicketHonCnt = sejPayment.GetOutput("X_ticket_hon_cnt");
   		// チケットバーコード番号_01
   		String sBarcodeNo = sejPayment.GetOutput("X_barcode_no_01");

   		// 戻り値出力
   		System.out.println("注文ID　　：" + sOrderId);
   		System.out.println("払込票番号：" + sHaraikomiNo);
   		System.out.println("払込票ID  ：" + sIraihyoId);
   	}
   }
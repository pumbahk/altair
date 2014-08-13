using System;
using NUnit.Framework;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.core
{
    
	[TestFixture()]
	public class FlowForEaglesTests
	{
		//認証後すぐにQR読み込み
		[Test, Description ("認証input画面 -ok-> password入力 -ok> auth情報取得 -ok-> QR読み込み")]
		public void TestAuthFlow ()
		{            
			var resource = new Resource ();

			var manager = new FlowManager (new EaglesFlowDefinition ());
			var startpoint = new CaseAuthInput (resource);

			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseAuthInput> (target.Case);

				// 認証処理
				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseAuthPassword> (target.Case);

				// 認証処理
				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseAuthDataFetch> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
			});
			t.Wait ();
		}

		// 1枚発券。まとめて発券選ばない
		[Test,Description ("eagles: QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました -ok-> QR読み込み")]
		public void TestItForAll__Eagles ()
		{
			var manager = new FlowManager (new EaglesFlowDefinition());
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRDataFetch> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRConfirmForAll> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CasePrintForOne), Is.False);
				Assert.IsInstanceOf<CasePrintForAll> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintFinish> (target.Case);

				// Finish. after redirect
				Assert.AreSame (InputUnit.qrcode.ToString (), target.GetFlowDefinition ().CurrentInputUnit.ToString ());

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
			});
			t.Wait ();
		}


		//必ずQRに戻る
		[Test, Description ("eagles 注文番号読み込み -ok-> 電話番号読み込み -ok-> 注文番号データのverify -ok-> Orderno表示(all) -ok-> 印刷(all) -ok-> 発券しました -ok-> QR読み込み")]
		public void TestItForOrderno_Eagles ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseOrdernoOrdernoInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition ().CurrentInputUnit = InputUnit.order_no;

			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoTelInput> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoVerifyRequestData> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoConfirmForAll> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CasePrintForOne), Is.False);
				Assert.IsInstanceOf<CasePrintForAll> (target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintFinish> (target.Case);

				// Finish. after redirect
				Assert.AreSame (InputUnit.order_no.ToString (), target.GetFlowDefinition ().CurrentInputUnit.ToString ());

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);
			});
			t.Wait ();
		}
	}

}

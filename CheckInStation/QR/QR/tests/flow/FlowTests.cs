using System;
using NUnit.Framework;
using System.Threading.Tasks;

namespace QR
{

	[TestFixture ()]
	public class FlowTests
	{
		[Test]
		public void TestManagerGetInternalEvent__AtleastEmptyEvent ()
		{
			var manager = new FlowManager ();
			manager.GetInternalEvent ();
		}

		[Test, Description ("認証input画面 -ok-> auth情報取得 -ok-> 認証方法選択")]
		public void TestAuthFlow ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseAuthInput (new Resource ());

			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseAuthInput>(target.Case);

				// 認証処理
				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseAuthDataFetch>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseInputStrategySelect>(target.Case);
			});
			t.Wait ();
		}

		[Test, Description ("認証方法選択画面 -qr-> QR読み込み")]
		public void TestInputSelectRedirectQRCode ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseInputStrategySelect (new Resource ());

			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start
				target.VerifyStatus = true;
				(target.Case as CaseInputStrategySelect).Unit = InputUnit.qrcode;

				target = await target.Forward () as FakeFlow;
				Assert.IsInstanceOf<CaseQRCodeInput>(target.Case);
			});
			t.Wait ();
		}


		[Test, Description ("認証方法選択画面 -order_no-> 注文番号読み込み")]
		public void TestInputSelectRedirectOrderno ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseInputStrategySelect (new Resource ());

			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start
				target.VerifyStatus = true;
				(target.Case as CaseInputStrategySelect).Unit = InputUnit.order_no;

				target = await target.Forward () as FakeFlow;
				Assert.IsInstanceOf<CaseOrdernoOrdernoInput>(target.Case);
			});
			t.Wait ();
		}

		/***********
		 * Orderno *
		 ***********/
		[Test, Description ("注文番号読み込み -ok-> 電話番号読み込み -ok-> 注文番号データのverify -ok-> Orderno表示(all) -ok-> 印刷(all) -ok-> 発券しました -ok-> 注文番号読み込み")]
		public void TestItForOrderno ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseOrdernoOrdernoInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition().CurrentInputUnit = InputUnit.order_no;
			
			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoOrdernoInput>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoTelInput>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoVerifyRequestData>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoConfirmForAll>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CasePrintForOne), Is.False);
				Assert.IsInstanceOf<CasePrintForAll>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintFinish>(target.Case);

				// Finish. after redirect
				Assert.AreSame(InputUnit.order_no.ToString(), target.GetFlowDefinition().CurrentInputUnit.ToString());

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseOrdernoOrdernoInput>(target.Case);
			});
			t.Wait ();
		}

		/***********
		 * QR      *
		 ***********/

		[Test, Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -ok-> 印刷(1枚) -ok> 発券しました -ok-> QR読み込み")]
		public void TestItForOne ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition().CurrentInputUnit = InputUnit.qrcode;

			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRDataFetch>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRConfirmForOne>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintForOne>(target.Case);
				Assert.That ((target.Case is CasePrintForAll), Is.False);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintFinish>(target.Case);

				// Finish. after redirect
				Assert.AreSame(InputUnit.qrcode.ToString(), target.GetFlowDefinition().CurrentInputUnit.ToString());

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput>(target.Case);
			});
			t.Wait ();
		}

		[Test,Description ("QR読み込み -ng-> エラー表示")]
		public void Test__QRInput__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			var t = Task.Run (async () => {
				target.VerifyStatus = false;
				target = await target.Forward () as FakeFlow;
				Assert.IsInstanceOf<CaseFailureRedirect>(target.Case);
			});
			t.Wait ();
		}

		[Test,Description ("印刷(1枚) -ng-> エラー表示")]
		public void Test__PrintForOne__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CasePrintForOne (new Resource (), null);
			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				target.VerifyStatus = false;
				target = await target.Forward () as FakeFlow;
				Assert.IsInstanceOf<CaseFailureRedirect>(target.Case);
			});
			t.Wait ();
		}

		[Test,Description ("印刷(all) -ng-> エラー表示")]
		public void Test__PrintForAll__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CasePrintForAll (new Resource (),null);
			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				target.VerifyStatus = false;
				target = await target.Forward () as FakeFlow;
				Assert.IsInstanceOf<CaseFailureRedirect>(target.Case);
			});
			t.Wait ();
		}

		[Test,Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚)[すべて印刷選択] -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました -ok-> QR読み込み")]
		public void TestItForAll ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition().CurrentInputUnit = InputUnit.qrcode;

			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRDataFetch>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRConfirmForOne>(target.Case);

				(target.Case as CaseQRConfirmForOne).Unit = PrintUnit.all;

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRConfirmForAll>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CasePrintForOne), Is.False);
				Assert.IsInstanceOf<CasePrintForAll>(target.Case);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CasePrintFinish>(target.Case);

				// Finish. after redirect
				Assert.AreSame(InputUnit.qrcode.ToString(), target.GetFlowDefinition().CurrentInputUnit.ToString());

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.IsInstanceOf<CaseQRCodeInput>(target.Case);
			});
			t.Wait ();
		}
	}
}


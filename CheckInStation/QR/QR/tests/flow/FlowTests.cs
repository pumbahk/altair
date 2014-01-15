using System;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;
using System.Threading.Tasks;

namespace QR
{
	class FakeFlow : Flow
	{
		public FakeFlow (FlowManager manager, ICase _case) : base (manager, _case)
		{
		}

		public bool VerifyStatus{ get; set; }

		public override Task ConfigureAsync ()
		{
			//ここでは詳細に触れない。
			return Task.Run (() => {
			});
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				return VerifyStatus;
			});
		}

		public override async Task<IFlow> Forward ()
		{
			var nextCase = await NextCase ();
			return new FakeFlow (Manager, nextCase);
		}
	}

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
		public void TestCase ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseAuthInput (new Resource ());

			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseAuthInput), Is.True);

				// 認証処理
				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseAuthDataFetch), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRInputStrategySelect), Is.True);
			});
			t.Wait ();
		}

		[Test, Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -ok-> 印刷(1枚) -ok> 発券しました")]
		public void TestItForOne ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRCodeInput), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRDataFetch), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRConfirmForOne), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRPrintForOne), Is.True);
				Assert.That ((target.Case is CaseQRPrintForAll), Is.False);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRPrintFinish), Is.True);
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
				Assert.That ((target.Case is CaseFailureRedirect), Is.True);
			});
			t.Wait ();
		}

		[Test,Description ("印刷(1枚) -ng-> エラー表示")]
		public void Test__PrintForOne__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRPrintForOne (new Resource (), null);
			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				target.VerifyStatus = false;
				target = await target.Forward () as FakeFlow;
				Assert.That ((target.Case is CaseFailureRedirect), Is.True);
			});
			t.Wait ();
		}

		[Test,Description ("印刷(all) -ng-> エラー表示")]
		public void Test__PrintForAll__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRPrintForAll (new Resource (),null);
			FakeFlow target = new FakeFlow (manager, startpoint);

			var t = Task.Run (async () => {
				target.VerifyStatus = false;
				target = await target.Forward () as FakeFlow;
				Assert.That ((target.Case is CaseFailureRedirect), Is.True);
			});
			t.Wait ();
		}

		[Test,Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚)[すべて印刷選択] -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました")]
		public void TestItForAll ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			var t = Task.Run (async () => {
				// start 
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRCodeInput), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRDataFetch), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRConfirmForOne), Is.True);

				(target.Case as CaseQRConfirmForOne).Unit = PrintUnit.all;

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRConfirmForAll), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRPrintForOne), Is.False);
				Assert.That ((target.Case is CaseQRPrintForAll), Is.True);

				target = await target.Forward () as FakeFlow;
				target.VerifyStatus = true;
				Assert.That ((target.Case is CaseQRPrintFinish), Is.True);
			});
			t.Wait ();
		}
	}
}


using NUnit.Framework;
using System;
using System.Threading.Tasks;

namespace QR
{
	[TestFixture ()]
	public class BackwardTests
	{
		[Test, Description ("QR印刷 -ok> 印刷完了しました -ok> QR読み込み -backward-> QR読み込み")]
		public void TestBackwardFromQRPrintFinished ()
		{
			var manager = new FlowManager ();
			var startpoint = new CasePrintFinish (new Resource (), null);
			FakeFlow target = new FakeFlow (manager, startpoint);

			// これは遷移時にすでに設定されている
			target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;
			manager.SetStartPoint (target);

			ICase result, case_;
			var t = Task.Run (async () => {
				// start 
				(manager.Peek () as FakeFlow).VerifyStatus = true;
				case_ = await manager.Forward ();
				Assert.IsInstanceOf<CaseQRCodeInput> (case_);

				/// 印刷後. backword.
				result = await manager.Backward ();
				Assert.IsInstanceOf<CaseQRCodeInput> (result);
			});
			t.Wait ();
		}

		[Test, Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -backword-> QR読み込み")]
		public void TestBackwordFromAuthForwarding ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new Resource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			// これは遷移時にすでに設定されている
			target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;
			manager.SetStartPoint (target);

			ICase result, case_;
			var t = Task.Run (async () => {
				// start 
				(manager.Peek () as FakeFlow).VerifyStatus = true;
				case_ = await manager.Forward ();
				Assert.IsInstanceOf<CaseQRDataFetch> (case_);

				(manager.Peek () as FakeFlow).VerifyStatus = true;
				case_ = await manager.Forward ();
				Assert.IsInstanceOf<CaseQRConfirmForOne> (case_);

				/// 印刷表示(1枚)
				result = await manager.Backward ();
				Assert.IsInstanceOf<CaseQRCodeInput> (result);
			});
			t.Wait ();
		}
	}
}


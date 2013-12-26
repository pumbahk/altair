using System;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	class FakeFlow : Flow
	{
		public FakeFlow (FlowManager manager, ICase _case) : base (manager, _case)
		{
		}

		public bool VerifyStatus{ get; set; }

		public override bool Verify ()
		{
			return VerifyStatus;
		}

		public override IFlow Forward ()
		{
			var nextCase = NextCase ();
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

		[Test, Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -ok-> 印刷(1枚) -ok> 発券しました")]
		public void TestItForOne ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new FakeResource ());
			FakeFlow target = new FakeFlow (manager, startpoint);
			
			// start 
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRCodeInput), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRDataFetch), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRConfirmForOne), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRPrintForOne), Is.True);
			Assert.That ((target.Case is CaseQRPrintForAll), Is.False);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRPrintFinish), Is.True);
		}

		[Test,Description ("QR読み込み -ng-> エラー表示")]
		public void Test__QRInput__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new FakeResource ());
			FakeFlow target = new FakeFlow (manager, startpoint);

			target.VerifyStatus = false;
			target = target.Forward () as FakeFlow;
			Assert.That ((target.Case is CaseFailureRedirect), Is.True);
		}

		[Test,Description ("印刷(1枚) -ng-> エラー表示")]
		public void Test__PrintForOne__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRPrintForOne (new FakeResource ());
			FakeFlow target = new FakeFlow (manager, startpoint);

			target.VerifyStatus = false;
			target = target.Forward () as FakeFlow;
			Assert.That ((target.Case is CaseFailureRedirect), Is.True);
		}

		[Test,Description ("印刷(all) -ng-> エラー表示")]
		public void Test__PrintForAll__Failure__DisplayError ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRPrintForAll (new FakeResource ());
			FakeFlow target = new FakeFlow (manager, startpoint);

			target.VerifyStatus = false;
			target = target.Forward () as FakeFlow;
			Assert.That ((target.Case is CaseFailureRedirect), Is.True);
		}

		[Test,Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚)[すべて印刷選択] -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました")]
		public void TestItForAll ()
		{
			var manager = new FlowManager ();
			var startpoint = new CaseQRCodeInput (new FakeResource ());
			FakeFlow target = new FakeFlow (manager, startpoint);

			// start 
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRCodeInput), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRDataFetch), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRConfirmForOne), Is.True);

			(target.Case as CaseQRConfirmForOne).Unit = PrintUnit.all;

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRConfirmForAll), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRPrintForOne), Is.False);
			Assert.That ((target.Case is CaseQRPrintForAll), Is.True);

			target = target.Forward () as FakeFlow;
			target.VerifyStatus = true;
			Assert.That ((target.Case is CaseQRPrintFinish), Is.True);
		}
	}
}


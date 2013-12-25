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
		[Test, Description("QR読み込み -ok-> QR表示(1枚) -ok-> 印刷(1枚) -ok> 発券しました")]
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

		[Test,Description("QR読み込み -ok-> QR表示(1枚)[すべて印刷選択] -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました")]
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


using System;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	//fake object
	[TestFixture ()]
	public class QRCodeInputTests
	{
		public CaseQRCodeInput target;

		[SetUp]
		public void SetupFixture ()
		{
			var loader = new FakeDataLoader<string> ("*qrcode*");
			var verifier = new FakeVerifier<string> (true);

			var resource = new Resource () {
				QRCodeLoader = loader,
				QRCodeVerifier = verifier
			};

			this.target = new CaseQRCodeInput (resource);
		}

		[Test ()]
		public void TestVerify ()
		{
			target.Configure (new QRInputEvent(){QRCode = "*qrcode*"});
			Assert.That (target.Verify (), Is.True);
			Assert.That (Is.Equals(target.QRCode, "*qrcode*"));
		}

		[Test ()]
		public void TestCallVerifyManyTimes ()
		{
			target.Configure (new QRInputEvent(){QRCode = "*qrcode*"});
			Assert.That (Is.Equals (target.VerifiedCount, 0));

			Assert.IsTrue (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));

			Assert.IsTrue (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));
		}

		[Test ()]
		public void TestCallVerifyManyTimes__False ()
		{
			target.Configure (new QRInputEvent(){QRCode = "*qrcode*"}); 
			FakeVerifier<string> v = target.QRCodeVerifier as FakeVerifier<string>;
			v.Result = false;

			Assert.That (Is.Equals (target.VerifiedCount, 0));

			Assert.IsFalse (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));

			Assert.IsFalse (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));
		}
	}
}
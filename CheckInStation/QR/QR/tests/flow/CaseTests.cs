using System;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	//fake object
	[TestFixture ()]
	public class CaseTests
	{
		public CaseQRCodeInput target;

		[SetUp]
		public void SetupFixture ()
		{
			var loader = new FakeDataLoader<string> ("*qrcode*");
			var verifier = new FakeVerifier<string> (true);

			var resource = new FakeResource () {
				QRCodeLoader = loader,
				QRCodeVerifier = verifier
			};

			this.target = new CaseQRCodeInput (resource);
		}

		[Test ()]
		public void TestVerify ()
		{
			target.Configure ();
			Assert.That (target.Verify (), Is.True);
			Assert.That (Is.Equals(target.QRCodeLoader.Result, "*qrcode*"));
		}

		[Test ()]
		public void TestCallVerifyManyTimes ()
		{
			target.Configure ();
			Assert.That (Is.Equals (target.VerifiedCount, 0));

			Assert.IsTrue (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));

			Assert.IsTrue (target.Verify ());
			Assert.That (Is.Equals (target.VerifiedCount, 1));
		}

		[Test ()]
		public void TestCallVerifyManyTimes__False ()
		{
			target.Configure (); 
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
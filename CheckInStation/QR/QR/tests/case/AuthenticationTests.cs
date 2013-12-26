using NUnit.Framework;
using System;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	[TestFixture ()]
	public class AuthenticationTests
	{
		[Test, Description ("認証情報入力部分. configureでloginnameとloginpassword取得")]
		public void TestAuthentcationInput__Configure__Setvalue ()
		{
			var resource = new Resource ();
			ICase target = new CaseAuthInput (resource);

			RequestBroker broker = new RequestBroker (new FlowManager ()); //hmm.
			broker.Event = new AuthenticationEvent ("*username*", "*password*");
			target.Configure (broker.GetInternalEvent ());

			Assert.AreEqual ("*username*", (target as CaseAuthInput).LoginName);
			Assert.AreEqual ("*password*", (target as CaseAuthInput).LoginPassword);
		}

		[Test, Description ("認証情報入力した後のvalidation. successした時")]
		public void TestAuthenticationInput__Verify__True__Get__Authenticator ()
		{
			var resource = new Resource ();
			var organization_id = "1";
			resource.Authentication = new FakeAuthentication ("*username*", "*password*", organization_id);

			CaseAuthInput target = new CaseAuthInput (resource) {
				LoginName = "*username*",
				LoginPassword = "*password*"
			};

			Assert.IsTrue (target.Verify ());
			Assert.IsNotNull (resource.AuthInfo);
		}

		[Test, Description ("認証情報入力した後のvalidation. failureした時エラーメッセージ")]
		public void TestAuthenticationInput__Verify__False__DisplayErrorMessage ()
		{
			var resource = new Resource ();
			var organization_id = "1";
			resource.Authentication = new FakeAuthentication ("x", "xx", organization_id);

			CaseAuthInput target = new CaseAuthInput (resource) {
				LoginName = "*username*",
				LoginPassword = "*password*",
				PresentationChanel = new AuthenticationEvent("","")
			};

			Assert.IsNull (target.PresentationChanel.ValidationErrorMessage);
			Assert.IsFalse (target.Verify ());
			Assert.IsNotNull (target.PresentationChanel.ValidationErrorMessage);
		}
	}
}


using NUnit.Framework;
using System;
using NUnit.Framework.SyntaxHelpers;
using System.Threading.Tasks;

namespace QR
{
	[TestFixture, Description ("AuthenticationInput")]
	public class AuthenticationTests
	{
		[Test, Description ("認証情報入力部分. configureでloginnameとloginpassword取得")]
		public void TestAuthentcationInput__ConfigureAsync__Setvalue ()
		{
			var resource = new Resource ();
			ICase target = new CaseAuthInput (resource);

			RequestBroker broker = new RequestBroker (new FlowManager ()); //hmm.
			broker.Event = new AuthenticationEvent ("*username*", "*password*");
			target.ConfigureAsync (broker.GetInternalEvent ());

			Assert.AreEqual ("*username*", (target as CaseAuthInput).LoginName);
			Assert.AreEqual ("*password*", (target as CaseAuthInput).LoginPassword);
		}
	}

	[TestFixture, Description ("AuthenticationDataFetch")]
	public class AuthenticaionFetchDataTests
	{
		[Test, Description ("認証情報入力した後のvalidation. successした時AuthInfoが取得できる")]
		public void TestAuthenticationInput__Verify__True__Get__AuthInfo ()
		{
			var resource = new Resource ();
			var inputUsername = "*username*";
			var inputPassword = "*password*";
			resource.Authentication = new FakeAuthentication (inputUsername, inputPassword);
			
			CaseAuthDataFetch target = new CaseAuthDataFetch (
				                           resource,
				                           inputUsername, 
				                           inputPassword);
			var t = Task.Run (async () => {
				var ev = new AuthenticationEvent (inputUsername, inputPassword);
				await target.ConfigureAsync (ev);
				Assert.IsTrue (await target.VerifyAsync ());
				ev.HandleEvent ();
				Assert.IsNotNull (resource.AuthInfo);
			});
			t.Wait ();
		}

		[Test, Description ("認証情報入力した後のvalidation. failureした時エラーメッセージ")]
		public void TestAuthenticationInput__Verify__False__DisplayErrorMessage ()
		{
			var resource = new Resource ();
			var inputUsername = "*username*";
			var inputPassword = "*password*";
			resource.Authentication = new FakeAuthentication ("x", "xx");

			CaseAuthDataFetch target = new CaseAuthDataFetch (
				                           resource,
				                           inputUsername, 
				                           inputPassword);
			var t = Task.Run (async () => {
				var ev = new AuthenticationEvent (inputUsername, inputPassword);
				await target.ConfigureAsync (ev);
				Assert.IsEmpty(ev.messages);
				Assert.IsFalse (await target.VerifyAsync ());
				Assert.IsNotEmpty(ev.messages);
			});
			t.Wait ();
		}
	}
}


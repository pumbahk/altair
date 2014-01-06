using NUnit.Framework;
using System;

namespace QR
{
	[TestFixture ()]
	public class AuthUsingTests
	{
		[Test, Description ("get login url")]
		public void TestsGetLoginURL ()
		{
			var resource = new Resource ();
			var result = new Authentication ().GetLoginURL (resource);

			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("login api called. response is endpoint")]
		public void TestCallLoginAPICheckResponseAsEndpoint ()
		{
			var mockContent = @"{""endpoint"": {""login_status"": ""http://login.status.url""}}";
			var resource = new Resource () {
				HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
			};
			var task = new Authentication ().TryLoginRequest (resource, "", "");
			task.Wait ();
			Assert.AreEqual (task.Result.LoginStatus, "http://login.status.url");
		}

		[Test, Description ("login api called. response is endpoint")]
		public void TestCallLoginAPIParseFailure ()
		{
			var mockContent = @"{""endpoint"": {""**"": ""http://login.status.url""}}";
			var resource = new Resource () {
				HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
			};
			var task = new Authentication ().TryLoginRequest (resource, "", "");
			try {
				task.Wait ();
			} catch {
			}
			Assert.IsNotNull (task.Exception);
			Assert.AreEqual (task.Exception.InnerException.GetType (), typeof(System.Xml.XmlException));
		}

		[Test,Description ("login status api called.")]
		public void TestCallLoginStatusAPI ()
		{
			var mockContent = @"{""login"": true,
 ""loginuser"": {""type"": ""login"",
		           ""id"": 1,
		           ""name"": ""operator.name""},
 ""organization"": {""id"": ""10""}}";
			var resource = new Resource () {
				HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
			};
			var task = new Authentication ().TryLoginStatusRequest (resource, "http://login.status.url");
			task.Wait ();
			Assert.AreEqual (task.Result.login, true);
			Assert.AreEqual (task.Result.organization_id, "10");
		}
	}
}


using NUnit.Framework;
using System;
using checkin.core.models;
using checkin.core.auth;
using checkin.core.message;
using checkin.core.web;

namespace checkin.core
{
    [TestFixture ()]
    public class AuthUsingTests
    {
        [Test, Description ("get login url")]
        public void TestsGetLoginURL ()
        {
            var resource = new Resource ();
            var result = new Authentication (resource, resource.GetLoginURL()).GetLoginURL ();

            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("login api called. response is endpoint")]
        public void TestCallLoginAPICheckResponseAsEndpoint ()
        {
            var mockContent = Testing.ReadFromEmbeddedFile ("QR.tests.misc.login.json");
            var resource = new Resource () {
                HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
            };
            var task = new Authentication (resource, resource.GetLoginURL()).TryLoginRequest ("", "");
            task.Wait ();
            StringAssert.Contains ("login.status.json", task.Result.LoginStatus);
        }

        [Test, Description ("login api called. failure")]
        public void TestCallLoginAPIParseFailure ()
        {
            var mockContent = @"{""endpoint"": {""**"": ""http://login.status.url""}}";
            var resource = new Resource () {
                HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
            };
            var task = new Authentication (resource, resource.GetLoginURL()).TryLoginRequest ("", "");
            try {
                task.Wait ();
            } catch {
            }
            Assert.IsNotNull (task.Exception);
            //Assert.AreEqual (typeof(System.Xml.XmlException), task.Exception.InnerException.GetType ());
        }

        [Test,Description ("login status api called.")]
        public void TestCallLoginStatusAPI ()
        {
            var mockContent = Testing.ReadFromEmbeddedFile ("QR.tests.misc.login.status.json");
            var resource = new Resource () {
                HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent)
            };
            var task = new Authentication (resource).TryLoginStatusRequest ("http://login.status.url");
            task.Wait ();
            Assert.AreEqual (task.Result.login, true);
            Assert.AreEqual (task.Result.organization_id, "10");
        }
    }
}


using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Linq;
using System.Net;

namespace checkin.core.web
{
    [TestFixture ()]
    public class ClientCreateTests
    {
        private IHttpWrapperFactory<HttpWrapper> target;

        [SetUp]
        public void Setup ()
        {
            target = new FakeHttpWrapperFactory<HttpWrapper> ("*dummy response*");
            IEnumerable<string> cookie_strings = new string[] {        
                "this", "is", "cookie", "string"
            };
            var cookies = cookie_strings.Select(s => new Cookie("http://localhost", s)).ToArray();
            target.AddCookies (cookies);
        }

        [Test, Description ("付加したcookieが取得可能")]
        public void TestCreateWithCookies__Gettable ()
        {
            var client = target.Create ("http://localhost").GetClient ();
            //httpclientからcookieContainerをとる方法がなさそう.
        }

        [Test, Description ("付加したクッキーが適切な文字列として保存されているかどうか")]
        public void TestCreateWithCookiew__CorrectString_Attached ()
        {
            var client = target.Create ("*dummy url*").GetClient ();
            IEnumerable<string> cookieBody;
            client.DefaultRequestHeaders.TryGetValues ("Cookie", out cookieBody);

            //IEnumetable<T>.ToList()が見つからない。。
            var attachedCookies = new List<string> ();
            foreach (var s in cookieBody) {
                attachedCookies.Add (s);
            }
            Assert.Contains ("this, is, cookie, string", attachedCookies);
        }
    }
}


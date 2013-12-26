using NUnit.Framework;
using System;
using NUnit.Framework.SyntaxHelpers;

namespace QR
{
	[TestFixture ()]
	public class FakeGetUrlTests
	{
		[Test ()]
		public void TestFake ()
		{
			var mockContent = "test-test-test";
			var factory = new FakeHttpWrapperFactory<HttpWrapper> (mockContent);
			using (var wrapper = factory.Create ("http://example.net"))
			using (var t = wrapper.GetStringAsync ()) {
				t.Wait ();
				Assert.That (Is.Equals (t.Result, "test-test-test"));
			}
		}
		
		//[Test ()] //実際にrequest投げてしまっているのでスキップ
		public void TestConcreate ()
		{
			var factory = new HttpWrapperFactory<HttpWrapper> ();
			using (var wrapper = factory.Create ("http://example.net"))
			using (var t = wrapper.GetStringAsync ()) {
				t.Wait ();
				Assert.IsTrue (t.Result.Contains ("<title>Example Domain</title>"));
			}
		}
	}
}

using NUnit.Framework;
using System;
using QR.message;

namespace QR
{
	[TestFixture ()]
	public class GetMessageFromAppConfigTests
	{
		[Test, Description ("login failure message")]
		public void TestsGetLoginFailureMessage ()
		{
			var resource = new Resource ();
			var result = resource.GetLoginFailureMessageFormat ();
			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("task canel message")]
		public void TestsGetTaskCancelMessage ()
		{
			var resource = new Resource ();
			var result = resource.GetTaskCancelMessage ();
			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("web exception message")]
		public void TestsGetWebExceptionMessage ()
		{
			var resource = new Resource ();
			var result = resource.GetWebExceptionMessage ();
			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("invalid input message")]
		public void TestsGetInvalidInputMessage ()
		{
			var resource = new Resource ();
			var result = resource.GetInvalidInputMessage ();
			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("invalid output message")]
		public void TestsGetInvalidOutputMessage ()
		{
			var resource = new Resource ();
			var result = resource.GetInvalidOutputMessage ();
			Assert.AreNotEqual (default(string), result);
		}
	}
}


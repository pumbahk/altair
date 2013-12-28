using NUnit.Framework;
using System;

namespace QR
{
	[TestFixture ()]
	public class GetMessageFromAppConfigTests
	{
		[Test, Description ("login failure message")]
		public void TestsGetLoginFailureMessage ()
		{
			var resource = new Resource ();
			var result = MessageResourceUtil.GetLoginFailureMessageFormat (resource);
			Assert.AreNotEqual (default(string), result);
		}

		[Test, Description ("task canel message")]
		public void TestsGetTaskCancelMessage ()
		{
			var resource = new Resource ();
			var result = MessageResourceUtil.GetTaskCancelMessage (resource);
			Assert.AreNotEqual (default(string), result);
		}
	}
}


using NUnit.Framework;
using System;

namespace QR
{
	[TestFixture ()]
	public class AuthUsingResourceInformationTests
	{
		[Test, Description ("login url")]
		public void TestsGetLoginURL ()
		{
			var resource = new Resource ();
			var result = new Authentication ().GetLoginURL (resource);

			Assert.AreNotEqual(default(string), result);
		}

		[Test, Description ("login status url")]
		public void TestsGetLoginStatusURL ()
		{
			var resource = new Resource ();
			var result = new Authentication ().GetLoginStatusURL (resource);

			Assert.AreNotEqual(default(string), result);
		}
	}
}


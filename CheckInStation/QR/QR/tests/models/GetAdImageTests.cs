using NUnit.Framework;
using System;

namespace QR
{
	[TestFixture ()]
	public class GetAdImageTests
	{
		[Test, Description("get ad image from 1 item")]
		public void TestImageFromItem()
		{
			var target = new AdImageCollector (new Resource ());
			var a = new byte[] { 0x20 };

			target.Add (a);
			target.State = CollectorState.ending;

			CollectionAssert.AreEqual (a, target.GetImage ());
			CollectionAssert.AreEqual (a, target.GetImage ());
			CollectionAssert.AreEqual (a, target.GetImage ());
		}
		[Test, Description("get ad image from 2items")]
		public void TestImageFrom2Items ()
		{
			var target = new AdImageCollector (new Resource ());
			var a = new byte[] { 0x20 };
			var b = new byte[] { 0x21 };

			target.Add (a);
			target.Add (b);
			target.State = CollectorState.ending;

			CollectionAssert.AreEqual (a, target.GetImage ());
			CollectionAssert.AreEqual (b, target.GetImage ());
			CollectionAssert.AreEqual (a, target.GetImage ());
		}
	}
}


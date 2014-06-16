using NUnit.Framework;
using System;
using checkin.core.models;

namespace checkin.core
{
    [TestFixture ()]
    public class GetAdImageTests
    {
        [Test, Description("get ad image from 1 item")]
        public void TestImageFromItem()
        {
            var target = new AdImageCollector (new Resource ());
            var a = target.CreateImage(new byte[] { 0x20 });

            target.Add (a);
            target.State = CollectorState.ending;

            Assert.AreSame (a, target.GetImage ());
            Assert.AreSame (a, target.GetImage ());
            Assert.AreSame (a, target.GetImage ());
        }
        [Test, Description("get ad image from 2items")]
        public void TestImageFrom2Items ()
        {
            var target = new AdImageCollector (new Resource ());
            var a = target.CreateImage(new byte[] { 0x20 });
            var b = target.CreateImage(new byte[] { 0x21 });

            target.Add (a);
            target.Add (b);
            target.State = CollectorState.ending;

            Assert.AreSame (a, target.GetImage ());
            Assert.AreSame (b, target.GetImage ());
            Assert.AreSame (a, target.GetImage ());
        }
    }
}


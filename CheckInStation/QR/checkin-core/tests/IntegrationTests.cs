using NUnit.Framework;
using System;
using System.Reflection;

namespace checkin.core
{

    [TestFixture ()]
    public class IntegrationTests
    {
        [Test ()]
        public void TestCase ()
        {

            var content = Testing.ReadFromEmbeddedFile ("QR.tests.misc.login.json");
            Console.WriteLine (content);
        }
    }
}


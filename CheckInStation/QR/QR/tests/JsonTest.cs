using System.Runtime.Serialization.Json;
using NUnit.Framework;
using System;
using System.IO;

namespace QR
{
	[TestFixture ()]
	public class JsonTest
	{
		[Test ()]
		public void TestCase ()
		{
			var qrsign = new QRSign () {
				qrcode = "*QR Sign*",
				region = "station1"
			};
			using (MemoryStream stream = new MemoryStream ()) {
				DataContractJsonSerializer ser = new DataContractJsonSerializer (typeof(QRSign));
				ser.WriteObject (stream, qrsign);
				stream.Position = 0;
				var result = new StreamReader (stream).ReadToEnd ();
				Assert.AreEqual (result, @"{""qrcode"":""*QR Sign*"",""region"":""station1""}");
			}
		}
	}
}


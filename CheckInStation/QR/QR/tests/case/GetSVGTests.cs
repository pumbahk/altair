using NUnit.Framework;
using System;
using System.Threading.Tasks;
using Codeplex.Data;

namespace QR
{
	[TestFixture ()]
	public class GetSVGTests
	{
		public class MockSVGImage : SVGImageFetcher
		{
			public MockSVGImage (IResource resource) : base (resource)
			{
			}

			public override string GetSvgOneURL ()
			{
				return "http://dummy.svg";
			}

			public override string GetImageFromSvgURL ()
			{
				return "http://dummy.image";
			}
		}

		[Test ()]
		public void TestsPrintingOneFetchSVGFromTIcketData ()
		{
			var t = Task.Run (async () => {
				var responseJSON = Testing.ReadFromEmbeddedFile ("QR.tests.misc.svgone.json");
				IResource resource = new Resource () {
					HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (responseJSON),
				};
				resource.SVGImageFetcher = new MockSVGImage (resource);

				var tdata = new TicketData (DynamicJson.Parse (Testing.ReadFromEmbeddedFile ("QR.tests.misc.qrdata.json")));
				ICase target = new CaseQRPrintForOne (resource, tdata);
				QRInputEvent ev = new QRInputEvent ();

				await target.ConfigureAsync (ev as IInternalEvent);
				//Console.WriteLine (await target.VerifyAsync ());
				//ev.HandleEvent ();
				Assert.IsTrue (await target.VerifyAsync ());
			});
			t.Wait ();
		}
	}
}


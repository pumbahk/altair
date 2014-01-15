using NUnit.Framework;
using System;
using System.Threading.Tasks;
using Codeplex.Data;

namespace QR
{
	[TestFixture ()]
	public class CaseRequestingJSONTests
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

		public class MockTDCollectionFetcher : TicketDataCollectionFetcher
		{
			public MockTDCollectionFetcher (IResource resource) : base (resource)
			{
			}

			public override string GetCollectionFetchUrl ()
			{
				return "http://dummy.ticketdata.all";
			}
		}

		[Test, Description ("QRconfirm all ticketdataからticketdata collectionを取ってくる")]
		public void TestsConfirmALlFecthTicketDataCollectionFromTicketData ()
		{
			var t = Task.Run (async () => {
				var responseJSON = Testing.ReadFromEmbeddedFile ("QR.tests.misc.qrdata.all.json");
				IResource resource = new Resource () {
					HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (responseJSON)
				};
				resource.TicketDataCollectionFetcher = new MockTDCollectionFetcher (resource);

				// case 初期化
				var tdata = new TicketData (DynamicJson.Parse (Testing.ReadFromEmbeddedFile ("QR.tests.misc.qrdata.json")));
				ICase target = new CaseQRConfirmForAll (resource, tdata);
				QRInputEvent ev = new QRInputEvent ();

				await target.ConfigureAsync (ev as IInternalEvent);
				//Console.WriteLine (await target.VerifyAsync ());
				//ev.HandleEvent ();

				Assert.IsTrue (await target.VerifyAsync ());
			});
			t.Wait ();
		}

		[Test, Description ("QR印刷1枚　ticketdataから券面のイメージを取ってくる")]
		public void TestsPrintingOneFetchSVGFromTIcketData ()
		{
			var t = Task.Run (async () => {
				var responseJSON = Testing.ReadFromEmbeddedFile ("QR.tests.misc.svgone.json");
				IResource resource = new Resource () {
					HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (responseJSON),
					TicketImagePrinting = new FakeTicketImagePrinting ()
				};
				resource.SVGImageFetcher = new MockSVGImage (resource);

				// case 初期化
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


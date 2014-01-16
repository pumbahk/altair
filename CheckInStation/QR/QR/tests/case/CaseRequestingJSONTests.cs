using NUnit.Framework;
using System;
using System.Threading.Tasks;
using Codeplex.Data;

namespace QR
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

		public override string GetSvgAllURL ()
		{
			return "http://dummy.all.svg";
		}

		public override string GetImageFromSvgURL ()
		{
			return "http://dummy.image";
		}
	}

	public class MockTDFetcher : TicketDataFetcher
	{
		public MockTDFetcher (IResource resource) : base (resource)
		{
		}

		public override string GetQRFetchDataUrl ()
		{
			return "http://dummy.ticketdata.all";
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

	[TestFixture ()]
	public class CaseRequestingJSONOrdernoTests
	{
		[Test, Description ("orderno confirm all verified order dataからticketdata collectionを取ってくる")]
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
				Console.WriteLine (await target.VerifyAsync ());
				ev.HandleEvent ();

				Assert.IsTrue (await target.VerifyAsync ());
			});
			t.Wait ();
		}
	}

	[TestFixture ()]
	public class CaseRequestingJSONQRCodeTests
	{
		[Test, Description ("QR fetch data qrcodeからticketdataを取ってくる")]
		public void TestsFecthTicketDataFromQRCode ()
		{
			var t = Task.Run (async () => {
				var responseJSON = Testing.ReadFromEmbeddedFile ("QR.tests.misc.qrdata.json");
				IResource resource = new Resource () {
					HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (responseJSON)
				};
				resource.TicketDataFetcher = new MockTDFetcher (resource);

				// case 初期化
				var qrcode = "*qrcode*";
				ICase target = new CaseQRDataFetch (resource, qrcode);
				QRInputEvent ev = new QRInputEvent ();

				await target.ConfigureAsync (ev as IInternalEvent);
				//Console.WriteLine (await target.VerifyAsync ());
				//ev.HandleEvent ();

				Assert.IsTrue (await target.VerifyAsync ());
			});
			t.Wait ();
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
				Console.WriteLine (await target.VerifyAsync ());
				ev.HandleEvent ();

				Assert.IsTrue (await target.VerifyAsync ());
			});
			t.Wait ();
		}

		[Test, Description ("QR印刷まとめて　ticketdata collectionから券面のイメージを取ってくる")]
		public void TestsPrintingAllFetchSVGFromTIcketDataCollection ()
		{
			var t = Task.Run (async () => {
				var responseJSON = Testing.ReadFromEmbeddedFile ("QR.tests.misc.svgall.json");
				IResource resource = new Resource () {
					HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper> (responseJSON),
					TicketImagePrinting = new FakeTicketImagePrinting ()
				};
				resource.SVGImageFetcher = new MockSVGImage (resource);

				// case 初期化
				var coll = new TicketDataCollection (DynamicJson.Parse (Testing.ReadFromEmbeddedFile ("QR.tests.misc.qrdata.all.json")));
				ICase target = new CasePrintForAll (resource, coll);
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
				ICase target = new CasePrintForOne (resource, tdata);
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


using System;

namespace QR
{
	public class QRConfiguration
	{
		public static void IncludeMe (IConfigurator config)
		{
			var resource = config.Resource;
			config.Resource.TicketDataFetcher = new TicketDataFetcher (resource);
			config.Resource.TicketDataCollectionFetcher = new TicketDataCollectionFetcher (resource);
			config.Resource.SVGImageFetcher = new SVGImageFetcher (resource);
			config.Resource.TicketImagePrinting = new FakeTicketImagePrinting ();
			config.Resource.TicketDataManager = new TicketDataManager (resource);
			config.Resource.VerifiedOrderDataFetcher = new VerifiedOrderDataFetcher (resource);
		}
	}
}


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
			config.Resource.SVGImageFetcher = new SVGImageFetcher (resource, new ImageFromSvgPostMultipart(resource)); //todo: change
			config.Resource.TicketImagePrinting = new TicketImagePrinting (resource);
			config.Resource.TicketDataManager = new TicketDataManager (resource);
			config.Resource.VerifiedOrderDataFetcher = new VerifiedOrderDataFetcher (resource);

			config.Resource.AdImageCollector = new AdImageCollector (resource);
		}
	}
}


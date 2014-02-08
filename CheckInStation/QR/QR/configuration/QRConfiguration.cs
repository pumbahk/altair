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

			// batik経由で券面データを画像として受け取る
			// config.Resource.SVGImageFetcher = new SVGTicketImageDataFetcher (resource, new ImageFromSvgPostMultipart(resource)); //todo: change

			// xamlとして返還された結果を受け取る
			config.Resource.SVGImageFetcher = new SVGTicketImageDataXamlFetcher (resource);

			config.Resource.TicketImagePrinting = new TicketImagePrinting (resource);
			config.Resource.TicketDataManager = new TicketDataManager (resource);
			config.Resource.VerifiedOrderDataFetcher = new VerifiedOrderDataFetcher (resource);

			config.Resource.AdImageCollector = new AdImageCollector (resource);
		}
	}
}


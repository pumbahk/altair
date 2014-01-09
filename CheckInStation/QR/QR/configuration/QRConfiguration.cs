using System;

namespace QR
{
	public class QRConfiguration
	{
		public static void IncludeMe (IConfigurator config)
		{
			config.Resource.TicketDataFetcher = new TicketDataFetcher (config.Resource);
			config.Resource.QRPrinting = new SVGImage (config.Resource);
		}
	}
}


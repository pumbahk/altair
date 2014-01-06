using System;

namespace QR
{
	public class QRConfiguration
	{
		public static void IncludeMe (IConfigurator config)
		{
			config.Resource.QRCodeVerifier = new QRCodeVerifier (config.Resource);
		}
	}
}


using System;

namespace QR
{
	public class QRConfiguration
	{
		public static void IncludeMe (IConfigurator config)
		{
			config.Resource.QRCodeLoader = new QRCodeLoader ();
			config.Resource.QRCodeVerifier = new QRCodeVerifier ();
		}
	}
}


using System;

namespace QR
{
	public class AuthConfiguration
	{
		public static void IncludeMe(IConfigurator config)
		{
			config.Resource.Authentication = new Authentication ();
		}
	}
}


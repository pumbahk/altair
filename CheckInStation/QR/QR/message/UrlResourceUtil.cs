using System;

namespace QR
{
	public static class UrlResourceUtil
	{
		public static string GetLoginURL (this IResource resource)
		{
			return resource.SettingValue ("endpoint.auth.login.url");
		}

		public static string GetMockLoginURL(this IResource resource)
		{
			return resource.SettingValue ("endpoint.mock.auth.login.url");
		}
	}
}


using System;
using System.Net.Http;

namespace QR
{
	public class HttpCommunicationConfiguration
	{
		public static void IncludeMe (IConfigurator config)
		{
			var factory = new HttpWrapperFactory<HttpWrapper> ();
			var timeout = TimeSpan.FromSeconds (1);
			Func<HttpClient,HttpClient> configure = (HttpClient client) => {
				client.Timeout = timeout;
				return client;
			};
			factory.ClientConfig = configure;
			config.Resource.HttpWrapperFactory = factory;

		}
	}
}


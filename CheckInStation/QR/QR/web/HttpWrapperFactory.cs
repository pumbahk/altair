using System;
using System.Net.Http;

namespace QR
{
	public class HttpWrapperFactory <T> : IHttpWrapperFactory<T>
		where T : IHttpWrapper, new()
	{
		public Func<HttpClient,HttpClient> ClientConfig { get; set; }

		public HttpClient CreateHttpClient ()
		{
			var client = new HttpClient ();
			if (ClientConfig != null) {
				client = ClientConfig (client);
			}
			return client;
		}

		public T Create (IUrlBuilder builder)
		{
			Func<HttpClient> factory = CreateHttpClient;
			return new T (){ ClientFactory = factory, UrlBuilder = builder };
		}

		public T Create (string url)
		{
			var builder = new TrasparentUrlBuilder (url);
			return Create (builder);
		}
	}
}
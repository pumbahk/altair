using System;
using System.Net.Http;

namespace QR
{
	public class FakeHttpWrapperFactory<T> :IHttpWrapperFactory<T>
		where T : IHttpWrapper, new()
	{
		public Func<HttpClient,HttpClient> ClientConfig { get; set; }

		public String MockContentString { get; set; }

		public FakeHttpWrapperFactory (String mockContentString)
		{
			MockContentString = mockContentString;
		}

		public HttpClient CreateHttpClient ()
		{
			var responseMessage = new HttpResponseMessage ();
			responseMessage.Content = new FakeHttpContent (this.MockContentString);
			var messageHandler = new FakeHttpMessageHandler (responseMessage);

			var client = new HttpClient (messageHandler);
			if (ClientConfig != null) {
				client = ClientConfig (client);
			}
			return client;
		}

		public T Create (string url)
		{
			var builder = new TrasparentUrlBuilder (url);
			return Create (builder);
		}

		public T Create (IUrlBuilder builder)
		{
			Func<HttpClient> factory = CreateHttpClient;
			return new T (){ ClientFactory = factory, UrlBuilder = builder };
		}
	}
}
using System;
using System.Net.Http;
using System.Collections.Generic;

namespace QR
{
	public class HttpWrapperFactory <T> : IHttpWrapperFactory<T>
		where T : IHttpWrapper, new()
	{
		public Func<HttpClient,HttpClient> ClientConfig { get; set; }

		protected List<string> cookies;

		public HttpWrapperFactory ()
		{
			cookies = new List<string> ();
		}

		public void AddCookies (IEnumerable<string> new_cookies)
		{
			foreach (var v in new_cookies) {
				cookies.Add (v);
			}
		}

		public void ClearCookies ()
		{
			cookies.Clear ();
		}
		// configuration client for individual usecase
		protected virtual HttpClient ClientAttachedSomething (HttpClient client)
		{
			if (ClientConfig != null) {
				client = ClientConfig (client);
			}
			CookieUtils.PutCokkiesToRequestHeaders (client.DefaultRequestHeaders, cookies);
			return client;
		}

		public virtual HttpClient CreateHttpClient ()
		{
			var client = new HttpClient ();
			return ClientAttachedSomething (client);
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
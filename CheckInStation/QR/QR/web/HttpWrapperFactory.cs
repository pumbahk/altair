using System;
using System.Net;
using System.Net.Http;
using System.Collections.Generic;

namespace QR
{
	public class HttpWrapperFactory <T> : IHttpWrapperFactory<T>
		where T : IHttpWrapper, new()
	{
		public Func<HttpClient,HttpClient> ClientConfig { get; set; }

        protected CookieContainer cookieContainer {get;set;}

		public HttpWrapperFactory ()
		{
			
		}

		public void AddCookies (IEnumerable<Cookie> new_cookies)
		{
            if (this.cookieContainer == null)
            {
                this.cookieContainer = new CookieContainer();
            }
			foreach (var v in new_cookies) {
                this.cookieContainer.Add(v);
			}
		}

        public void AddCookies(CookieContainer container)
        {
            if (this.cookieContainer == null)
            {
                this.cookieContainer = container;
            }
            else
            {
                throw new NotImplementedException("sorry. not supported yet");
            }
        }

		public void ClearCookies ()
		{
            this.cookieContainer = null;
		}

		// configuration client for individual usecase
		protected virtual HttpClient ClientAttachedSomething (HttpClient client)
		{
			if (ClientConfig != null) {
				client = ClientConfig (client);
			}
			return client;
		}

		public virtual HttpClient CreateHttpClient ()
		{
            var handler = new HttpClientHandler();
            CookieUtils.PutCokkiesToRequestHandler(handler, this.cookieContainer);
			var client = new HttpClient (handler);
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
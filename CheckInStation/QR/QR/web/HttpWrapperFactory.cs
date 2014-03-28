using System;
using System.Net;
using System.Net.Http;
using System.Collections.Generic;
using NLog;

namespace QR
{
    public class HttpWrapperFactory <T> : IHttpWrapperFactory<T>
        where T : IHttpWrapper, new()
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

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
                logger.Warn("this is not invalid behavior. overwrited via new container.");
                this.cookieContainer = container;
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
            //temporary: 
            var handler = new HttpClientHandler() { Credentials = new NetworkCredential("mock", "mock") };
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
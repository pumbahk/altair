using System;
using System.Net;
using System.Net.Http;
using System.Collections.Generic;
using NLog;
using System.Security.Cryptography.X509Certificates;
using System.Net.Security;
using checkin.core.support;

namespace checkin.core.web
{
    public class HttpWrapperFactory <T> : IHttpWrapperFactory<T>
        where T : IHttpWrapper, new()
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

        public Func<HttpClient,HttpClient> ClientConfig { get; set; }

        protected CookieContainer cookieContainer {get;set;}
        public Func<CookieContainer,HttpClientHandler> HandlerFactory { get; set; }
        public HttpWrapperFactory ()
        {
            this.HandlerFactory = DefaultHandlerFactory;
        }

        public HttpWrapperFactory(Func<CookieContainer,HttpClientHandler> handlerFactory,
                                  Func<HttpClient, HttpClient> clientConfigure)
        {
            this.HandlerFactory = handlerFactory;
            this.ClientConfig = clientConfigure;
        }

        public static HttpClientHandler DefaultHandlerFactory(CookieContainer cookieContainer)
        {
            var cache = new CredentialCache();
            var handler = new HttpClientHandler() { Credentials = cache };
            CookieUtils.PutCokkiesToRequestHandler(handler, cookieContainer);
            return handler;
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
                logger.Warn("this is not invalid behavior. overwrited via new container.".WithMachineName());
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
            var client = new HttpClient (this.HandlerFactory(this.cookieContainer));
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
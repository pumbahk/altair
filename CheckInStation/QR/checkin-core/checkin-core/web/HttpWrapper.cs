using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Threading;
using System.IO;
using NLog;
using checkin.core.support;

namespace checkin.core.web
{
    public class HttpWrapper :IHttpWrapper
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();
        
        //todo: 
        public static int RetryMaxCount = 3;
        public static TimeSpan RetryDelay = TimeSpan.FromMilliseconds(300);
        
        public async Task<T> RetryAsyncCall<T>(Func<Task<T>> thunk, string uri, int retryMax){
            int i = 0;
        RETRY:
            try{
                i++;
                return await thunk();
            }
            catch
            {
                if (i > retryMax)
                {
                    throw;
                }
                logger.Warn("request failure. retry(i={0}), url={1}, Delay={2}".WithMachineName(), i, uri, HttpWrapper.RetryDelay);
            }


            if (i <= retryMax) {
                await Task.Delay(HttpWrapper.RetryDelay);
            }
            goto RETRY;
        }

        public Task<T> RetryAsyncCall<T>(Func<Task<T>> thunk, string uri){
            return this.RetryAsyncCall(thunk, uri, HttpWrapper.RetryMaxCount);
        }


        public async Task<string> ReadAsStringAsync(HttpContent content)
        {
            var result = await content.ReadAsStringAsync().ConfigureAwait(false);
            logger.Trace("* API Output:{0}".WithMachineName(), result);
            return result;
        }
        
        public Task<Stream> ReadAsStreamAsync(HttpContent content)
        {
            //todo. remove await;
            return content.ReadAsStreamAsync();
        }


        protected HttpClient client;

        public Func<HttpClient> ClientFactory { get; set; }

        public IUrlBuilder UrlBuilder { get; set; }

        public HttpWrapper ()
        {
            //Don't use this, casually. (this is existed for generic new constraint)
        }

        public HttpClient GetClient ()
        {
            if (this.client != null) {
                throw new InvalidOperationException ("used by another something, already.");
            }
            this.client = this.ClientFactory ();
            return client;
        }

        public HttpWrapper (Func<HttpClient> clientFactory, IUrlBuilder builder)
        {
            this.ClientFactory = clientFactory;
            this.UrlBuilder = builder;
        }

        public HttpWrapper (Func<HttpClient> clientFactory, string url)
        {
            this.ClientFactory = clientFactory;
            this.UrlBuilder = new TrasparentUrlBuilder (url);
        }

        public void Dispose ()
        {
            try
            {
                if (client != null)
                {
                    //logger.Debug("begin dispose!".WithMachineName());
                    client.Dispose();
                    //logger.Debug@("end dispose!".WithMachineName());
                }
                client = null;
            }
            catch (Exception e)
            {
                logger.ErrorException("dispose".WithMachineName(), e);
                throw;
            }
        }

        public Task<HttpResponseMessage> GetAsync ()
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.GetAsync (url), url);
        }

        public Task<HttpResponseMessage> GetAsync (CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.GetAsync (url, ct), url);
        }

        public Task<Stream> GetStreamAsync ()
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<Stream>(() => client.GetStreamAsync (url), url);
        }

        public async Task<String> GetStringAsync ()
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            var result = await client.GetStringAsync (url);
            logger.Trace("* API Output:{0}".WithMachineName(), result);
            return result;
        }

        public Task<HttpResponseMessage> DeleteAsync ()
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.DeleteAsync(url), url);
        }

        public Task<HttpResponseMessage> DeleteAsync (CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.DeleteAsync (url, ct), url);
        }

        public Task<HttpResponseMessage> PostAsync (HttpContent content)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PostAsync (url, content), url);
        }

        public Task<HttpResponseMessage> PostAsync (HttpContent content, CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PostAsync (url, content, ct), url);
        }

        public Task<HttpResponseMessage> PutAsync (HttpContent content)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PutAsync (url, content), url);
        }

        public Task<HttpResponseMessage> PutAsync (HttpContent content, CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PutAsync (url, content, ct), url);
        }

        public Task<HttpResponseMessage> PostAsJsonAsync<T> (T value)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PostAsJsonAsync<T> (url, value), url);
        }

        public Task<HttpResponseMessage> PostAsJsonAsync<T> (T value, CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PostAsJsonAsync<T> (url, value, ct), url);
        }

        public Task<HttpResponseMessage> PutAsJsonAsync<T> (T value)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PutAsJsonAsync<T> (url, value), url);
        }

        public Task<HttpResponseMessage> PutAsJsonAsync<T> (T value, CancellationToken ct)
        {
            var client = this.GetClient ();
            var url = this.UrlBuilder.Build ();
            return this.RetryAsyncCall<HttpResponseMessage>(() => client.PutAsJsonAsync<T> (url, value, ct), url);
        }
    }
}

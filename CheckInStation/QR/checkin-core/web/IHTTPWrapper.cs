using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Threading;
using System.IO;

namespace checkin.core.web
{
    public interface IHttpWrapper :IDisposable
    {
        Func<HttpClient> ClientFactory { get; set; }

        IUrlBuilder UrlBuilder { get; set; }

        Task<HttpResponseMessage> GetAsync ();

        Task<HttpResponseMessage> GetAsync (CancellationToken token);

        Task<Stream> GetStreamAsync ();

        Task<String> GetStringAsync ();

        Task<HttpResponseMessage> DeleteAsync ();

        Task<HttpResponseMessage> DeleteAsync (CancellationToken token);

        Task<HttpResponseMessage> PostAsync (HttpContent content);

        Task<HttpResponseMessage> PostAsync (HttpContent content, CancellationToken token);

        Task<HttpResponseMessage> PutAsync (HttpContent content);

        Task<HttpResponseMessage> PutAsync (HttpContent content, CancellationToken token);

        Task<HttpResponseMessage> PostAsJsonAsync<T> (T Value);

        Task<HttpResponseMessage> PostAsJsonAsync<T> (T Value, CancellationToken token);

        Task<HttpResponseMessage> PutAsJsonAsync<T> (T Value);

        Task<HttpResponseMessage> PutAsJsonAsync<T> (T Value, CancellationToken token);

    }
}


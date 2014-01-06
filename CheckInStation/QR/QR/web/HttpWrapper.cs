using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Threading;
using System.IO;


namespace QR
{
	public class HttpWrapper :IHttpWrapper
	{
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
			if (client != null) {
				client.Dispose ();
				//System.Console.WriteLine ("Dispose!");
			}
			client = null;
		}

		public async Task<HttpResponseMessage> GetAsync ()
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.GetAsync (url);
		}

		public async Task<HttpResponseMessage> GetAsync (CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.GetAsync (url, ct);
		}

		public async Task<Stream> GetStreamAsync ()
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.GetStreamAsync (url);
		}

		public async Task<String> GetStringAsync ()
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			//TODO:change to debug log
			var result = await client.GetStringAsync (url);
			Console.WriteLine("Output:{0}", result);
			return result;
		}

		public async Task<HttpResponseMessage> DeleteAsync ()
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.DeleteAsync (url);
		}

		public async Task<HttpResponseMessage> DeleteAsync (CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.DeleteAsync (url, ct);
		}

		public async Task<HttpResponseMessage> PostAsync (HttpContent content)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PostAsync (url, content);
		}

		public async Task<HttpResponseMessage> PostAsync (HttpContent content, CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PostAsync (url, content, ct);
		}

		public async Task<HttpResponseMessage> PutAsync (HttpContent content)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PutAsync (url, content);
		}

		public async Task<HttpResponseMessage> PutAsync (HttpContent content, CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PutAsync (url, content, ct);
		}

		public async Task<HttpResponseMessage> PostAsJsonAsync<T> (T value)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PostAsJsonAsync<T> (url, value);
		}

		public async Task<HttpResponseMessage> PostAsJsonAsync<T> (T value, CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PostAsJsonAsync<T> (url, value, ct);
		}

		public async Task<HttpResponseMessage> PutAsJsonAsync<T> (T value)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PutAsJsonAsync<T> (url, value);
		}

		public async Task<HttpResponseMessage> PutAsJsonAsync<T> (T value, CancellationToken ct)
		{
			var client = this.GetClient ();
			var url = this.UrlBuilder.Build ();
			return await client.PutAsJsonAsync<T> (url, value, ct);
		}

	}
}

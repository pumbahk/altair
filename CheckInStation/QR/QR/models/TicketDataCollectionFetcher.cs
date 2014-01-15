using System;
using System.Threading.Tasks;
using QR.message;
using System.Net.Http;
using Codeplex.Data;

namespace QR
{
	public class TicketDataCollectionFetcher : IDataFetcher<TicketData, TicketDataCollection>
	{
		public IResource Resource { get; set; }

		public TicketDataCollectionFetcher (IResource resource)
		{
			this.Resource = resource;
		}

		public string GetCollectionFetchUrl ()
		{
			return Resource.EndPoint.DataCollectionFetchData;
		}

		public async Task<ResultTuple<string, TicketDataCollection>> FetchAsync (TicketData tdata)
		{
			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetCollectionFetchUrl ())) {
				var prams = new {order_no = tdata.order_no};
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (prams).ConfigureAwait (false)) {
					return Parse (
						await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false),
						tdata);
				}
			}
		}

		public ResultTuple<string, TicketDataCollection> Parse (string responseString, TicketData tdata)
		{
			try {
				var json = DynamicJson.Parse (responseString);
				return new Success<string, TicketDataCollection> (new TicketDataCollection (json, tdata));
			} catch (System.Xml.XmlException) {
				//hmm. log?
				return new Failure<string, TicketDataCollection> (Resource.GetInvalidInputMessage ());
			}
		}
	}
}

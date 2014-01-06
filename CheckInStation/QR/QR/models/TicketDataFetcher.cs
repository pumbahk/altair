using System;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using QR.message;

namespace QR
{
	public class TicketDataFetcher : IDataFetcher<string, TicketData>
	{
		public IResource Resource { get; set; }

		public TicketData TicketData { get; set; }

		public class QRRequest
		{
			public string qrsigned{ get; set; }
		}

		public TicketDataFetcher (IResource resource)
		{
			Resource = resource;
		}

		public string GetQRFetchDataUrl ()
		{
			return Resource.EndPoint.QRFetchData;
		}

		public async Task<ResultTuple<string, TicketData>> FetchAsync (string qrcode)
		{
			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetQRFetchDataUrl ())) {
				var qrdata = new QRRequest (){ qrsigned = qrcode };
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (qrdata).ConfigureAwait (false)) {
					return Parse (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
				}
			}
		}

		public ResultTuple<string, TicketData> Parse (string responseString)
		{
			try {
				var json = DynamicJson.Parse (responseString);
				return new Success<string, TicketData> (new TicketData (json));
			} catch (System.Xml.XmlException) {
				//hmm. log?
				return new Failure<string, TicketData> (Resource.GetInvalidInputMessage ());
			}
		}
	}
}


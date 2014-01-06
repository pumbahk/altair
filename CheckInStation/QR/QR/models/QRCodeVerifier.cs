using System;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;

namespace QR
{
	public class QRCodeVerifier : IVerifier<string>
	{
		public IResource Resource { get; set; }

		public TicketData TicketData { get; set; }

		public class QRRequest
		{
			public string qrsigned{ get; set; }
		}

		public QRCodeVerifier (IResource resource)
		{
			Resource = resource;
		}

		public bool Verify (string qrcode)
		{
			return false; //TODO:implement
		}

		public string GetQRFetchDataUrl ()
		{
			return Resource.EndPoint.QRFetchData;
		}

		public async Task<bool> VerifyAsync (string qrcode)
		{
			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetQRFetchDataUrl ())) {
				var qrdata = new QRRequest (){ qrsigned = qrcode };
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (qrdata).ConfigureAwait (false)) {
					return Parse (await response.Content.ReadAsStringAsync ().ConfigureAwait (false));
				}
			}
		}

		public bool Parse (string responseString)
		{
			try {
				var json = DynamicJson.Parse (responseString);
				TicketData = new TicketData (json);
				return true;
			} catch (System.Xml.XmlException) {
				//hmm. log?
				return false;
			}
		}
	}
}


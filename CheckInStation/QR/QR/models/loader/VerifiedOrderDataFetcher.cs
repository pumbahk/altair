using System;
using NLog;
using QR.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;

namespace QR
{
	public class VerifiedOrderDataFetcher: IDataFetcher<OrdernoRequestData, VerifiedOrdernoRequestData>
	{
		public IResource Resource { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public VerifiedOrderDataFetcher (IResource resource)
		{
			this.Resource = resource;
		}

		public virtual string GetVerifyURL ()
		{
			return Resource.EndPoint.VerifyOrderData;
		}

		public async Task<ResultTuple<string, VerifiedOrdernoRequestData>> FetchAsync (OrdernoRequestData requestData)
		{
			IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
			using (var wrapper = factory.Create (GetVerifyURL ())) {
				using (HttpResponseMessage response = await wrapper.PostAsJsonAsync (requestData).ConfigureAwait (false)) {
					return Parse (await wrapper.ReadAsStringAsync (response.Content).ConfigureAwait (false));
				}
			}
		}

		public ResultTuple<string, VerifiedOrdernoRequestData> Parse (string responseString)
		{
			try {
				var json = DynamicJson.Parse (responseString);
				return new Success<string, VerifiedOrdernoRequestData> (new VerifiedOrdernoRequestData(json));
			} catch (System.Xml.XmlException e) {
				logger.ErrorException (":", e);
				return new Failure<string, VerifiedOrdernoRequestData> (Resource.GetInvalidInputMessage ());
			}
		}
	}
}


using System;
using NLog;
using QR.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using System.IO;
using QR.support;

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
            using (var wrapper = factory.Create(GetVerifyURL()))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(requestData).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));

            }
        }

        public ResultTuple<string, VerifiedOrdernoRequestData> Parse (Stream response)
        {
            try {
                var json = DynamicJson.Parse (response);
                return new Success<string, VerifiedOrdernoRequestData> (new VerifiedOrdernoRequestData(json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":", e);
                return new Failure<string, VerifiedOrdernoRequestData> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}


using System;
using NLog;
using checkin.core.message;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using System.IO;
using checkin.core.support;
using checkin.core.web;

namespace checkin.core.models
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
                logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetVerifyURL(), json.ToString());
                return new Success<string, VerifiedOrdernoRequestData> (new VerifiedOrdernoRequestData(json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string, VerifiedOrdernoRequestData> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}


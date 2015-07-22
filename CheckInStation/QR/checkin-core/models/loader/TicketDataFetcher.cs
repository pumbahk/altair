using System;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using checkin.core.message;
using NLog;
using System.IO;
using checkin.core.support;
using checkin.core.web;

namespace checkin.core.models
{
    public class TicketDataFetcher : IDataFetcher<string, TicketData>
    {
        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketData TicketData { get; set; }

        public class QRRequest
        {
            public string qrsigned { get; set; }
            public bool refreshMode { get; set; }
        }

        public TicketDataFetcher (IResource resource)
        {
            Resource = resource;
        }

        public virtual string GetQRFetchDataUrl ()
        {
            return Resource.EndPoint.QRFetchData;
        }

        public async Task<ResultTuple<string, TicketData>> FetchAsync(string qrcode)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetQRFetchDataUrl()))
            {
                var qrdata = new QRRequest() { qrsigned = qrcode, refreshMode = this.Resource.RefreshMode };
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(qrdata).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
            }

        }

        public ResultTuple<string, TicketData> Parse (Stream response)
        {
            try {
                var json = DynamicJson.Parse (response);
                logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetQRFetchDataUrl(), json.ToString());
                return new Success<string, TicketData> (new TicketData (json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string, TicketData> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}


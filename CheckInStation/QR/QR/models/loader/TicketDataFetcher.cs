using System;
using System.Threading.Tasks;
using System.Net.Http;
using Codeplex.Data;
using QR.message;
using NLog;
using System.IO;
using QR.support;

namespace QR
{
    public class TicketDataFetcher : IDataFetcher<string, TicketData>
    {
        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketData TicketData { get; set; }

        public class QRRequest
        {
            public string qrsigned{ get; set; }
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
                var qrdata = new QRRequest() { qrsigned = qrcode };
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(qrdata).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
            }

        }

        public ResultTuple<string, TicketData> Parse (Stream response)
        {
            try {
                var json = DynamicJson.Parse (response);
                return new Success<string, TicketData> (new TicketData (json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":", e);
                return new Failure<string, TicketData> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}


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

        public class QRSkidataRequest : QRRequest
        {
            public string qrdata { get; set; }
        }

        public TicketDataFetcher (IResource resource)
        {
            Resource = resource;
        }

        public virtual string GetQRFetchDataUrl (bool isSkidata)
        {
            if (isSkidata)
            {
                return Resource.EndPoint.QRSkidataFetchData;
            }
            return Resource.EndPoint.QRFetchData;
        }

        public QRRequest getRequestData(bool isSkidata, string qrcode)
        {
            return isSkidata ? new QRSkidataRequest() { qrdata = qrcode, refreshMode = this.Resource.RefreshMode } 
                             : new QRRequest() { qrsigned = qrcode, refreshMode = this.Resource.RefreshMode };
        }

        public async Task<ResultTuple<string, TicketData>> FetchAsync(string qrcode)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            bool isSkidata = qrcode.Length == 20;
            using (var wrapper = factory.Create(GetQRFetchDataUrl(isSkidata)))
            {
#if DEBUG
                Console.WriteLine("isSkidata: " + isSkidata);
                Console.WriteLine("qrcode: " + qrcode);
                Console.WriteLine("URL: " + wrapper.UrlBuilder.Build());
#endif
                var qrdata = getRequestData(isSkidata, qrcode);
#if DEBUG
                Console.WriteLine("Request data: " + qrdata.ToString());
#endif
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(qrdata).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                return Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false), isSkidata);
            }

        }

        public ResultTuple<string, TicketData> Parse (Stream response, bool isSkidata)
        {
            try {
                var json = DynamicJson.Parse (response);
#if DEBUG
                Console.WriteLine("Response data: " + json);
#endif
                logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetQRFetchDataUrl(isSkidata), json.ToString());
                return new Success<string, TicketData> (new TicketData (json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string, TicketData> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}


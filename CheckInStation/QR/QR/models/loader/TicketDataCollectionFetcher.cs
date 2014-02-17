using System;
using System.Threading.Tasks;
using QR.message;
using System.Net.Http;
using Codeplex.Data;
using NLog;

namespace QR
{
    public class TicketDataCollectionFetcher : IDataFetcher<TicketDataCollectionRequestData, TicketDataCollection>
    {
        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketDataCollectionFetcher (IResource resource)
        {
            this.Resource = resource;
        }

        public virtual string GetCollectionFetchUrl ()
        {
            return Resource.EndPoint.DataCollectionFetchData;
        }

        public async Task<ResultTuple<string, TicketDataCollection>> FetchAsync(TicketDataCollectionRequestData requestData)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetCollectionFetchUrl()))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(requestData).ConfigureAwait(false);
                response.EnsureSuccessStatusCode();
                return Parse(await wrapper.ReadAsStringAsync(response.Content).ConfigureAwait(false));
            }
        }

        public ResultTuple<string, TicketDataCollection> Parse (string responseString)
        {
            try {
                var json = DynamicJson.Parse (responseString);
                return new Success<string, TicketDataCollection> (new TicketDataCollection (json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":", e);
                return new Failure<string, TicketDataCollection> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}

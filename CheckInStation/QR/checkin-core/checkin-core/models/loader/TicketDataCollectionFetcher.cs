using System;
using System.Threading.Tasks;
using checkin.core.message;
using System.Net.Http;
using Codeplex.Data;
using NLog;
using System.IO;
using checkin.core.support;
using checkin.core.web;

namespace checkin.core.models
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
                response.EnsureSuccessStatusCodeExtend();
                return Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
            }
        }

        public ResultTuple<string, TicketDataCollection> Parse (Stream response)
        {
            try {
                var json = DynamicJson.Parse(response);
                logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetCollectionFetchUrl(), json.ToString());
                return new Success<string, TicketDataCollection> (new TicketDataCollection (json));
            } catch (System.Xml.XmlException e) {
                logger.ErrorException (":".WithMachineName(), e);
                return new Failure<string, TicketDataCollection> (Resource.GetInvalidInputMessage ());
            }
        }
    }
}

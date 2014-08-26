using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Net.Http;
using NLog;
using checkin.core.message;
using checkin.core.support;
using checkin.core.web;

namespace checkin.core.models
{
	public class TicketPrintedAtUpdater
	{
		public IResource Resource { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public TicketPrintedAtUpdater (IResource resource)
		{
			Resource = resource;
		}

		public virtual string GetUpdatePrintedAtURL ()
		{
			return Resource.EndPoint.UpdatePrintedAt;
		}

        public async Task<bool> UpdatePrintedAtAsync(UpdatePrintedAtRequestData data)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            using (var wrapper = factory.Create(GetUpdatePrintedAtURL()))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                var responseResult = await wrapper.ReadAsStringAsync(response.Content).ConfigureAwait(false);
                logger.Info("*API Response* method=GET, url={0}, data={1}".WithMachineName(), this.GetUpdatePrintedAtURL(), responseResult);                
                return true;
            }
        }
	}
}


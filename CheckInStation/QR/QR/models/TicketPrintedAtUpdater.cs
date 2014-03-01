using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Net.Http;
using NLog;
using QR.message;
using QR.support;

namespace QR
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
                await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false);
                return true;
            }
        }
	}
}


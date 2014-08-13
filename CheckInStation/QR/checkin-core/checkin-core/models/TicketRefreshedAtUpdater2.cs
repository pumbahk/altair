using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NLog;
using System.Net.Http;
using checkin.core.support;
using Codeplex.Data;
using checkin.core.message;
using checkin.core.web;

namespace checkin.core.models
{
    public class TicketRefreshedAtUpdater2
    {
         public IResource Resource { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public TicketRefreshedAtUpdater2 (IResource resource)
		{
			Resource = resource;
		}

		public virtual string GetUpdateRefreshedAtURL ()
		{
            return Resource.EndPoint.UpdateRefreshedAt2;
		}

        public class OrdernoRequest
        {
            public string order_no { get; set; }
            public string tel { get; set; }
        }

        public async Task<ResultTuple<string, string>> UpdateRefreshedAtAsync(string order_no, string tel)
        {
            IHttpWrapperFactory<HttpWrapper> factory = Resource.HttpWrapperFactory;
            var data = new OrdernoRequest() { order_no=order_no, tel=tel};
            using (var wrapper = factory.Create(GetUpdateRefreshedAtURL()))
            {
                HttpResponseMessage response = await wrapper.PostAsJsonAsync(data).ConfigureAwait(false);
                response.EnsureSuccessStatusCodeExtend();
                try
                {
                    var json = DynamicJson.Parse(await wrapper.ReadAsStreamAsync(response.Content).ConfigureAwait(false));
                    logger.Info("*API Response* method=POST, url={0}, data={1}".WithMachineName(), this.GetUpdateRefreshedAtURL(), json.ToString());                
                    return new Success<string, string>(json.order_no);
                }
                catch (System.Xml.XmlException e)
                {
                    logger.ErrorException(":".WithMachineName(), e);
                    return new Failure<string, string>(Resource.GetInvalidInputMessage());
                }
            }
        }
    }
}

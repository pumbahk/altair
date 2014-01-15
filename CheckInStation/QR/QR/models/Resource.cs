using System;
using System.Configuration;
using System.Net.Http;
using NLog;

namespace QR
{
	public class Resource :IResource
	{
		protected bool VerifyEnable;
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public Resource (bool verifyEnable)
		{
			this.VerifyEnable = verifyEnable;
		}

		public Resource ()
		{
			this.VerifyEnable = false;
		}

		public bool Verify ()
		{
			if (VerifyEnable) {
				return this.FullVerify ();
			} else {
				return true;
			}
		}

		public bool FullVerify ()
		{
			if (TicketDataFetcher == null)
				throw new InvalidOperationException ("TicketDataFetcher is NULL");
			if (TicketDataCollectionFetcher == null)
				throw new InvalidOperationException ("TicketDataCollectionFetcher is NULL");
			if (TicketDataManager == null)
				throw new InvalidOperationException ("TicketDataManager is NULL");
			if (SVGImageFetcher == null)
				throw new InvalidOperationException ("SVGImageFetcher is null");
			if (TicketImagePrinting == null)
				throw new InvalidOperationException ("TicketImagePrinting is null");
			if (Authentication == null)
				throw new InvalidOperationException ("Authentication is null");
			if (HttpWrapperFactory == null)
				throw new InvalidOperationException ("HttpWrapperFactory is null");
			return true;
		}

		public IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

		public IDataFetcher<TicketData, TicketDataCollection> TicketDataCollectionFetcher { get; set; }

		public TicketDataManager TicketDataManager { get; set; }

		public SVGImageFetcher SVGImageFetcher{ get; set; }

		public ITicketImagePrinting TicketImagePrinting{ get; set; }

		public EndPoint EndPoint { get; set; }

		public AuthInfo AuthInfo { get; set; }

		public IAuthentication Authentication { get; set; }

		public IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }

		public string SettingValue (string key)
		{
			var v = ConfigurationManager.AppSettings [key];
			logger.Debug ("get from resource: {0}", v);
			return v;
		}
	}
}


using System;
using System.Configuration;
using System.Net.Http;

namespace QR
{
	public class Resource :IResource
	{
		protected bool VerifyEnable;

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
			if (QRPrinting == null)
				throw new InvalidOperationException ("QRPrinting is null");
			if (Authentication == null)
				throw new InvalidOperationException ("Authentication is null");
			if (HttpWrapperFactory == null)
				throw new InvalidOperationException ("HttpWrapperFactory is null");
			return true;
		}

		public IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

		public SVGImage QRPrinting{ get; set;}

		public EndPoint EndPoint { get; set; }

		public AuthInfo AuthInfo { get; set; }

		public IAuthentication Authentication { get; set; }

		public IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }

		public string SettingValue (string key)
		{
			var v = ConfigurationManager.AppSettings [key];
			Console.WriteLine ("    *debug get: {0}", v);
			return v;
		}
	}
}


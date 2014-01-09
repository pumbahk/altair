using System;
using System.Net.Http;

namespace QR
{
	public interface INeedForQR
	{
		IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }
		SVGImage QRPrinting {get;set;}
	}

	public interface INeedForAuth
	{
		IAuthentication Authentication{ get; set; }

		AuthInfo AuthInfo{ get; set; }

		IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }
	}
	//本当は分割した形で管理したい
	public interface IResource : INeedForQR, INeedForAuth
	{
		bool Verify ();

		EndPoint EndPoint { get; set; }

		string SettingValue (string key);
	}
}


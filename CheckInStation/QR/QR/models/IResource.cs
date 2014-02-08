using System;
using System.Net.Http;

namespace QR
{
	public interface INeedForQR
	{
		IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

		IDataFetcher<TicketDataCollectionRequestData, TicketDataCollection> TicketDataCollectionFetcher { get; set; }

		IDataFetcher<OrdernoRequestData, VerifiedOrdernoRequestData> VerifiedOrderDataFetcher{ get; set; }

		ISVGTicketImageDataFetcher SVGImageFetcher { get; set; }

		ITicketPrinting TicketPrinting { get; set; }

		TicketPrintedAtUpdater TicketDataManager { get; set; }

		AdImageCollector AdImageCollector { get; set; }
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

        string GetUniqueNameEachMachine();
	}
}


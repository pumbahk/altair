using System;
using System.Net.Http;

namespace QR
{
    public interface IResource
    {

        bool Verify();

        EndPoint EndPoint { get; set; }

        //認証用
        IAuthentication Authentication { get; set; }

        AuthInfo AuthInfo { get; set; }

        //アプリ用
        IModelValidation Validation { get; set; }

        IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

        IDataFetcher<TicketDataCollectionRequestData, TicketDataCollection> TicketDataCollectionFetcher { get; set; }

        IDataFetcher<OrdernoRequestData, VerifiedOrdernoRequestData> VerifiedOrderDataFetcher { get; set; }

        ISVGTicketImageDataFetcher SVGImageFetcher { get; set; }

        ITicketPrinting TicketPrinting { get; set; }

        TicketPrintedAtUpdater TicketDataManager { get; set; }

        AdImageCollector AdImageCollector { get; set; }


        IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }


        string SettingValue(string key);
        int WaitingTimeAfterFinish { get; set; } // 印刷完了後の待ち時間(ミリ秒)
        string GetUniqueNameEachMachine();
    }
}


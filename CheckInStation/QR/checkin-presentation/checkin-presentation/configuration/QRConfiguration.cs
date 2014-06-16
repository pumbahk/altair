using System;
using checkin.core.models;
using checkin.presentation.models;
using checkin.core;

namespace checkin.config
{
    public class QRConfiguration
    {
        public static void SetupPrinting_Image(IResource resource)
        {
            // batik経由で券面データを画像として受け取る
            resource.SVGImageFetcher = new SVGTicketImageDataByteArrayFetcher (resource, new ImageFromSvgPostMultipart(resource)); //todo: change
            resource.TicketPrinting = new TicketImagePrinting(resource);
        }

        public static void SetupPrinting_Xaml(IResource resource)
        {
            // xamlとして返還された結果を受け取る
            resource.SVGImageFetcher = new SVGTicketImageDataXamlFetcher(resource);
            resource.TicketPrinting = new TicketXamlPrinting(resource);
        }

        public static void IncludeMe (IConfigurator config)
        {
            var resource = config.Resource;
            QRConfiguration.SetupPrinting_Xaml(resource);
            config.Resource.Validation = new ModelValidation();
            config.Resource.TicketDataFetcher = new TicketDataFetcher (resource);
            config.Resource.TicketDataCollectionFetcher = new TicketDataCollectionFetcher (resource);


            config.Resource.TicketDataManager = new TicketPrintedAtUpdater (resource);
            config.Resource.VerifiedOrderDataFetcher = new VerifiedOrderDataFetcher (resource);

            config.Resource.AdImageCollector = new AdImageCollector (resource);

            //印刷後の待ち時間設定
            resource.WaitingTimeAfterFinish = Convert.ToInt32(resource.SettingValue("waittime.after.finish.millisec"));
        }
    }
}


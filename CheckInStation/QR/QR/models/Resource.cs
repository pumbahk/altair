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
            this.WaitingTimeAfterFinish = 30;
        }

        public Resource ()
        {
            this.VerifyEnable = false;
            this.WaitingTimeAfterFinish = 30;
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
            if (Validation == null)
                throw new InvalidOperationException ("Validation is null");
            if (TicketDataFetcher == null)
                throw new InvalidOperationException ("TicketDataFetcher is NULL");
            if (TicketDataCollectionFetcher == null)
                throw new InvalidOperationException ("TicketDataCollectionFetcher is NULL");
            if (TicketDataManager == null)
                throw new InvalidOperationException ("TicketDataManager is NULL");
            if (VerifiedOrderDataFetcher == null)
                throw new InvalidOperationException ("VerifiedOrderDataFetcher is NULL");
            if (SVGImageFetcher == null)
                throw new InvalidOperationException ("SVGImageFetcher is null");
            if (TicketPrinting == null)
                throw new InvalidOperationException ("TicketImagePrinting is null");
            if (Authentication == null)
                throw new InvalidOperationException ("Authentication is null");
            if (AdImageCollector == null)
                throw new InvalidOperationException ("AdImageCollector is null");
            if (HttpWrapperFactory == null)
                throw new InvalidOperationException ("HttpWrapperFactory is null");
            return true;
        }
        public IModelValidation Validation { get; set; }

        public IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

        public IDataFetcher<TicketDataCollectionRequestData, TicketDataCollection> TicketDataCollectionFetcher { get; set; }

        public IDataFetcher<OrdernoRequestData, VerifiedOrdernoRequestData> VerifiedOrderDataFetcher{ get; set; }

        public TicketPrintedAtUpdater TicketDataManager { get; set; }

        public ISVGTicketImageDataFetcher SVGImageFetcher{ get; set; }

        public ITicketPrinting TicketPrinting{ get; set; }

        public EndPoint EndPoint { get; set; }

        public AuthInfo AuthInfo { get; set; }

        public IAuthentication Authentication { get; set; }

        public AdImageCollector AdImageCollector { get; set; }

        public IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }

        public int WaitingTimeAfterFinish { get; set; }

        public string SettingValue (string key)
        {
            var v = ConfigurationManager.AppSettings [key];
            logger.Trace ("get from resource: key={0} value={1}", key, v);
            return v;
        }

        public string GetUniqueNameEachMachine()
        {
            return System.Environment.MachineName;
        }
    }
}


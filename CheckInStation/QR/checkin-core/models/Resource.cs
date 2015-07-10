using System;
using System.Configuration;
using System.Net.Http;
using NLog;
using checkin.core.support;
using checkin.core.web;
using checkin.core.flow;
using checkin.core.events;
using checkin.core.auth;
namespace checkin.core.models
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
            this.RefreshMode = false;
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
            //if (FlowDefinition == null)
            //    throw new InvalidOperationException("FlowDefinition is  null");
            return true;
        }

        public bool MultiPrintMode { get; set; }

        public bool RefreshMode { get; set; }

        public IModelValidation Validation { get; set; }

        public IDataFetcher<string, TicketData> TicketDataFetcher { get; set; }

        public IDataFetcher<TicketDataCollectionRequestData, TicketDataCollection> TicketDataCollectionFetcher { get; set; }

        public IDataFetcher<OrdernoRequestData, VerifiedOrdernoRequestData> VerifiedOrderDataFetcher{ get; set; }

        public TicketPrintedAtUpdater TicketDataManager { get; set; }

        public ISVGTicketImageDataFetcher SVGImageFetcher{ get; set; }

        public ITicketPrinting TicketPrinting{ get; set; }

        public EndPoint EndPoint { get; set; }

        public AuthInfo AuthInfo { get; set; }

        public LoginUser LoginUser { get; set; }

        public IAuthentication Authentication { get; set; }

        public AdImageCollector AdImageCollector { get; set; }

        public IHttpWrapperFactory<HttpWrapper> HttpWrapperFactory { get; set; }

        public int WaitingTimeAfterFinish { get; set; }

        public IFlowDefinition FlowDefinition { get; set; }

        public string SettingValue (string key)
        {
            var v = ConfigurationManager.AppSettings [key];
            logger.Trace ("get from resource: key={0} value={1}".WithMachineName(), key, v);
            return v;
        }

        public string GetUniqueNameEachMachine()
        {
            return EnvironmentName.GetMachineName();
        }

        public bool IsEnableAnotherMode()
        {
            return this.SettingValue("application.enable.anothermode").ToLower() == "true";
        }
    }
}


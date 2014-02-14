using System;
using System.Threading.Tasks;
using NLog;
using QR.message;

namespace QR
{
    /// <summary>
    /// Case CaseOrdernoVerifyRequestData. 注文番号データのverify
    /// </summary>
    public class CaseOrdernoVerifyRequestData : AbstractCase, ICase, IAutoForwardingCase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public OrdernoRequestData RequestData { get; set; }

        public VerifiedOrdernoRequestData VerifiedData { get; set; }

        public TicketDataCollection Collection { get; set; }

        public CaseOrdernoVerifyRequestData (IResource resource, OrdernoRequestData data) : base (resource)
        {
            this.RequestData = data;
        }

        public override async Task<bool> VerifyAsync ()
        {
            try {
                ResultTuple<string, VerifiedOrdernoRequestData> result = await Resource.VerifiedOrderDataFetcher.FetchAsync (this.RequestData);
                if (result.Status) {
                    this.VerifiedData = result.Right;
                    return true;
                } else {
                    //modelからpresentation層へのメッセージ

                    PresentationChanel.NotifyFlushMessage ((result as Failure<string,VerifiedOrdernoRequestData>).Result);
                    return false;
                }
            } catch (Exception ex) {
                logger.ErrorException (":", ex);
                PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
                return false;
            }
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseOrdernoConfirmForAll (this.Resource, this.VerifiedData);
        }
    }
}


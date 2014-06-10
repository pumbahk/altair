using System;
using QR.message;
using System.Threading.Tasks;
using NLog;
using System.Collections.Generic;
using QR.support;

namespace QR
{
    /// <summary>
    /// Case Orderno confirm for all. Orderno表示(all)
    /// </summary>
    // 
    public class CaseOrdernoConfirmForAll: AbstractCase,ICase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public VerifiedOrdernoRequestData RequestData { get; set; }

        public TicketDataCollection Collection { get; set; }

        protected TokenStatus tokenStatus;

        public CaseOrdernoConfirmForAll (IResource resource, VerifiedOrdernoRequestData requestData) : base (resource)
        {
            this.RequestData = requestData;
            this.tokenStatus = TokenStatus.valid;
        }

        public override async Task PrepareAsync(IInternalEvent ev)
        {
            await base.PrepareAsync(ev).ConfigureAwait(false);
            var data = new TicketDataCollectionRequestData()
            {
                order_no = this.RequestData.order_no,
                secret = this.RequestData.secret
            };
            ResultTuple<string, TicketDataCollection> result = await new DispatchResponse<TicketDataCollection>(Resource).Dispatch(() => Resource.TicketDataCollectionFetcher.FetchAsync(data)).ConfigureAwait(false);
            if (result.Status)
            {
                this.Collection = result.Right;
                this.tokenStatus = result.Right.status;

                var subject = this.PresentationChanel as ConfirmAllEvent;
                subject.SetCollection(this.Collection);
            }
            else
            {
                //modelからpresentation層へのメッセージ
                PresentationChanel.NotifyFlushMessage((result as Failure<string, TicketDataCollection>).Result);
                this.tokenStatus = TokenStatus.unknown;
            }
        }

        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                return this.tokenStatus == TokenStatus.valid;
            });
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CasePrintForAll (Resource, this.Collection);
        }

        public override ICase OnFailure (IFlow flow)
        {
            flow.Finish ();
            logger.Warn(String.Format("invalid status: status={0}, order_no={1}".WithMachineName(), this.tokenStatus.ToString(), this.RequestData.order_no));
            var message = this.Resource.GetTokenStatusMessage(this.tokenStatus);
            return new CaseFailureRedirect(Resource, message);
        }
    }
}


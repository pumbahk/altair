using System;
using checkin.core.message;
using System.Threading.Tasks;
using NLog;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case QR confirm for all. QR表示(all)
    /// </summary>
    // 
    public class CaseQRConfirmForAll: AbstractCase,ICase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketData TicketData { get; set; }

        protected TokenStatus tokenStatus;

        public TicketDataCollection TicketDataCollection { get; set; }

        public int PartOrAll { get; set; }

        public CaseQRConfirmForAll (IResource resource, TicketData ticketdata) : base (resource)
        {
            TicketData = ticketdata;
            this.tokenStatus = TokenStatus.valid;
            this.Resource = resource;
            this.PartOrAll = 1;
        }

        public CaseQRConfirmForAll(IResource resource, TicketData ticketdata, int partorall)
            : base(resource)
        {
            TicketData = ticketdata;
            this.tokenStatus = TokenStatus.valid;
            this.Resource = resource;
            this.PartOrAll = partorall;
        }

        public override async Task PrepareAsync(IInternalEvent ev)
        {
            await base.PrepareAsync(ev).ConfigureAwait(false);

            var subject = ev as ConfirmAllEvent;
            var data = new TicketDataCollectionRequestData() { order_no = TicketData.additional.order.order_no, secret = TicketData.secret, refreshMode = this.Resource.RefreshMode };
            subject.SetInfo(TicketData);

            ResultTuple<string, TicketDataCollection> result = await new DispatchResponse<TicketDataCollection>(Resource).Dispatch(() => Resource.TicketDataCollectionFetcher.FetchAsync(data)).ConfigureAwait(false);
            if (result.Status)
            {
                this.TicketDataCollection = result.Right;
                this.tokenStatus = this.TicketDataCollection.status;
                subject.SetCollection(result.Right);
                subject.SetPartOrAll(this.PartOrAll);
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
            return Task.Run (() => this.tokenStatus == TokenStatus.valid);
        }

        public override ICase OnFailure(IFlow flow)
        {
            flow.Finish();
            logger.Warn("invalid status: status={0}, token_id={1}".WithMachineName(), this.tokenStatus.ToString(), this.TicketData.ordered_product_item_token_id);
            var message = this.Resource.GetTokenStatusMessage(this.tokenStatus);
            return new CaseFailureRedirect(Resource, message);
        }

        public override ICase OnSuccess (IFlow flow)
        {
            //return new CasePrintForAll (Resource, TicketDataCollection);
            return new CaseConfirmListForAll(Resource);
        }
    }
}


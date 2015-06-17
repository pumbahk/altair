using System;
using System.Threading.Tasks;
using checkin.core.message;
using NLog;
using checkin.core.support;
using checkin.core.flow;
using checkin.core;
using checkin.core.events;
using checkin.core.models;

namespace checkin.core.flow
{
    /// <summary>
    /// Case QR data fetch. QRからデータ取得中
    /// </summary>
    public class CaseQRDataFetch : AbstractCase, ICase, IAutoForwardingCase
    {
        public string QRCode { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        private TokenStatus tokenStatus;

        public TicketData TicketData { get; set; }

        public AggregateShorthandError TreatShorthandError { get; set; }

        public CaseQRDataFetch (IResource resource, string qrcode) : base (resource)
        {
            QRCode = qrcode;
            tokenStatus = TokenStatus.valid;
        }

        public override async Task<bool> VerifyAsync()
        {
            ResultTuple<string, TicketData> result = await new DispatchResponse<TicketData>(Resource).Dispatch(() => Resource.TicketDataFetcher.FetchAsync(this.QRCode)).ConfigureAwait(false);
            if (result.Status)
            {
                this.TicketData = result.Right;
                if (this.TicketData.Verify())
                {
                    return true;
                }
                else
                {
                    this.tokenStatus = this.TicketData.status;
                    return false;
                }
            }
            else
            {
                //modelからpresentation層へのメッセージ
                this.TreatShorthandError = new AggregateShorthandError(this.PresentationChanel);
                this.TreatShorthandError.Parse(result.Left);
                return false;
            }
        }

        public override ICase OnFailure (IFlow flow)
        {
            //flow.Finish ();
            if (this.tokenStatus == TokenStatus.valid)
            {
                if (this.TreatShorthandError != null)
                {
                    return this.TreatShorthandError.Redirect(flow);
                }
                else
                {
                    return base.OnFailure(flow);
                }
            }
            logger.Error("invalid status: status={0}, token_id={1}".WithMachineName(), this.tokenStatus.ToString(), this.TicketData.ordered_product_item_token_id);
            var message = this.Resource.GetTokenStatusMessage (this.tokenStatus);
            return new CaseFailureRedirect(Resource, message);
        }

        public override ICase OnSuccess(IFlow flow)
        {
            return flow.GetFlowDefinition ().AfterQRDataFetch (Resource, TicketData);
        }
    }
}


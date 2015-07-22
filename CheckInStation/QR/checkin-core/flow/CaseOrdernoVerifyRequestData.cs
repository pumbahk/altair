using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.message;
using checkin.core.support;
using checkin.core.flow;
using checkin.core.models;

namespace checkin.core.flow
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

        public AggregateShorthandError TreatShorthandError { get; set; }

        public CaseOrdernoVerifyRequestData (IResource resource, OrdernoRequestData data) : base (resource)
        {
            this.RequestData = data;
        }

        public override async Task<bool> VerifyAsync()
        {
            ResultTuple<string, VerifiedOrdernoRequestData> result = await new DispatchResponse<VerifiedOrdernoRequestData>(Resource).Dispatch(() =>
            {
                return Resource.VerifiedOrderDataFetcher.FetchAsync(this.RequestData);
            }).ConfigureAwait(false);
            if (result.Status)
            {
                this.VerifiedData = result.Right;
                return true;
            }
            else
            {
                //modelからpresentation層へのメッセージ
                this.TreatShorthandError = new AggregateShorthandError(this.PresentationChanel);
                this.TreatShorthandError.Parse(result.Left);
                return false;
            }
        }

        public override ICase OnSuccess (IFlow flow)
        {
            //return new CaseOrdernoConfirmForAll (this.Resource, this.VerifiedData);
            return flow.GetFlowDefinition().AfterOrdernoConfirmed(this.Resource, this.VerifiedData);
        }

        public override ICase OnFailure(IFlow flow)
        {
            if (this.TreatShorthandError != null)
            {
                return this.TreatShorthandError.Redirect(flow);
            }
            return base.OnFailure(flow);
        }
    }
}


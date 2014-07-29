using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case CaseOrdernoOrdernoInput. 
    /// </summary>
    public class CaseOrdernoOrdernoInput : AbstractCase, ICase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public OrdernoRequestData RequestData { get; set; }

        public CaseOrdernoOrdernoInput (IResource resource) : base (resource)
        {
            this.RequestData = new OrdernoRequestData ();
        }

        public override Task<bool> VerifyAsync ()
        {
            var ts = new TaskCompletionSource<bool>();
            var subject = this.PresentationChanel as OrdernoInputEvent;
            this.RequestData.order_no = subject.Orderno;
            var r = this.Resource.Validation.ValidateOrderno(this.RequestData.order_no, subject.OrganizationCode);
            ts.SetResult(r.Status);
            if (!r.Status)
            {
                this.PresentationChanel.NotifyFlushMessage(r.Left);
            }
            return ts.Task;            
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseOrdernoTelInput(Resource, RequestData);
        }

        public override ICase OnFailure (IFlow flow)
        {
            return this;
        }
    }
}

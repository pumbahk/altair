using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case CaseOrdernoTelInput. 電話番号読み込み
    /// </summary>
    public class CaseOrdernoTelInput : AbstractCase, ICase, IAutoForwardingCase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public OrdernoRequestData RequestData { get; set; }

        public CaseOrdernoTelInput (IResource resource, OrdernoRequestData data) : base (resource)
        {
            this.RequestData = data;
        }

        public override Task<bool> VerifyAsync ()
        {
            var subject = this.PresentationChanel as OrdernoInputEvent;
            this.RequestData.tel = subject.Tel;
            var ts = new TaskCompletionSource<bool>();
            var r = this.Resource.Validation.ValidateTel(this.RequestData.tel);
            ts.SetResult(r.Status);
            if(!r.Status){
                this.PresentationChanel.NotifyFlushMessage(r.Left);
            }
            return ts.Task;
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseOrdernoVerifyRequestData (this.Resource, this.RequestData);
        }

        public override ICase OnFailure (IFlow flow)
        {
            return this;
        }
    }
}

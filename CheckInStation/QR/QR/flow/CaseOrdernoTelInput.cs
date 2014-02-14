using System;
using System.Threading.Tasks;
using NLog;

namespace QR
{
    /// <summary>
    /// Case CaseOrdernoTelInput. 電話番号読み込み
    /// </summary>
    public class CaseOrdernoTelInput : AbstractCase, ICase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public OrdernoRequestData RequestData { get; set; }

        public CaseOrdernoTelInput (IResource resource, OrdernoRequestData data) : base (resource)
        {
            this.RequestData = data;
        }

        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                var subject = this.PresentationChanel as OrdernoInputEvent;
                this.RequestData.tel = subject.Tel;
                return this.RequestData.tel != null;
            });
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseOrdernoVerifyRequestData (this.Resource, this.RequestData);
        }

        public override ICase OnFailure (IFlow flow)
        {
            PresentationChanel.NotifyFlushMessage ("failure");
            return this;
        }
    }
}

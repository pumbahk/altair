using System;
using System.Threading.Tasks;
using checkin.core.message;
using checkin.core.events;
using checkin.core.models;

namespace checkin.core.flow
{
    /// <summary>
    /// Case QR code input. QR読み込み
    /// </summary>
    /// 
    public class CaseQRCodeInput : AbstractCase, ICase
    {
        public string QRCode { get; set; }

        public override Task<bool> VerifyAsync()
        {
            var ts = new TaskCompletionSource<bool>();
            var ev = this.PresentationChanel as QRInputEvent;
            this.QRCode = ev.QRCode;
            var r = this.Resource.Validation.ValidateQRCode(this.QRCode);
            ts.SetResult(r.Status);
            if (!r.Status)
            {
                PresentationChanel.NotifyFlushMessage(r.Left);
            }
            return ts.Task;
        }

        public CaseQRCodeInput(IResource resource)
            : base(resource)
        {
        }

        public override ICase OnSuccess(IFlow flow)
        {
            return new CaseQRDataFetch(Resource, QRCode);
        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}


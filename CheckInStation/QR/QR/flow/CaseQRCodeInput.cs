using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
    /// <summary>
    /// Case QR code input. QR読み込み
    /// </summary>
    /// 
    public class CaseQRCodeInput :AbstractCase, ICase
    {
        public string QRCode { get; set; }

        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                QRInputEvent subject = this.PresentationChanel as QRInputEvent;
                this.QRCode = subject.QRCode;
                return this.QRCode != null && this.QRCode != "";
            });
        }

        public CaseQRCodeInput (IResource resource) : base (resource)
        {
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseQRDataFetch (Resource, QRCode);
        }

        public override ICase OnFailure (IFlow flow)
        {
            PresentationChanel.NotifyFlushMessage ("failure");
            return this;
        }
    }
}


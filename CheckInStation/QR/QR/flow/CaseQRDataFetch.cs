using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case QR data fetch. QRからデータ取得中
	/// </summary>
	public class CaseQRDataFetch : AbstractCase, ICase
	{
		public string QRCode { get; set; }
		public TicketData TicketData { get; set; }
		public CaseQRDataFetch (IResource resource, string qrcode) : base (resource)
		{
			QRCode = qrcode;
		}

		public override bool Verify ()
		{
			Task<bool> t = Resource.QRCodeVerifier.VerifyAsync (QRCode);
			try {
				t.Wait (); //TODO:xxxx:
			} catch (AggregateException ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (Resource.GetTaskCancelMessage());
				return false;
			}
			if (!t.Result) {
				PresentationChanel.NotifyFlushMessage ("heh");
			}
			return t.Result;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRConfirmForOne (Resource);
		}
	}
}


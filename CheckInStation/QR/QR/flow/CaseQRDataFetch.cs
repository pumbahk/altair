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

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, TicketData> result = await Resource.TicketDataFetcher.FetchAsync (this.QRCode);
				if (result.Status) {
					this.TicketData = result.Right;
					return true;
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,TicketData>).Result);
					return false;
				}
			} catch (Exception ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRConfirmForOne (Resource);
		}
	}
}


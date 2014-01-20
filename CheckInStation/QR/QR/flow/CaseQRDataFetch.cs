using System;
using System.Threading.Tasks;
using QR.message;
using NLog;

namespace QR
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

		public CaseQRDataFetch (IResource resource, string qrcode) : base (resource)
		{
			QRCode = qrcode;
			tokenStatus = TokenStatus.valid;
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, TicketData> result = await Resource.TicketDataFetcher.FetchAsync (this.QRCode);
				if (result.Status) {
					this.TicketData = result.Right;
					if (this.TicketData.Verify ()) {
						return true;
					} else {
						this.tokenStatus = this.TicketData.status;
						return false;
					}
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,TicketData>).Result);
					return false;
				}
			} catch (Exception ex) {
				logger.ErrorException (":", ex);
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public ICase OnFailure (IFlow flow, string message)
		{
			flow.Finish ();
			return new CaseFailureRedirect (Resource, message);
		}

		public override ICase OnSuccess (IFlow flow)
		{
			if (this.tokenStatus == TokenStatus.valid) {
				return new CaseQRConfirmForOne (Resource, TicketData);
			} else {
				logger.Error (String.Format ("invalid status: status={0}, token_id={1}", this.tokenStatus.ToString (), this.TicketData.ordered_product_item_token_id));
				return this.OnFailure (flow, this.Resource.GetTokenStatusMessage (this.tokenStatus));
			}
		}
	}
}


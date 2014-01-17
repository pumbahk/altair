using System;
using System.Threading.Tasks;
using QR.message;
using NLog;

namespace QR
{
	public enum TokenStatus
	{
		valid,
		canceled,
		printed,
		unknown
	}

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
						this.tokenStatus = TokenStatus.unknown; //TODO:適切なenum
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

		public override ICase OnSuccess (IFlow flow)
		{
			if (this.tokenStatus == TokenStatus.valid) {
				return new CaseQRConfirmForOne (Resource, TicketData);
			} else {
				logger.Error ("dataError:"); //TODO:まじめに処理書く
				return base.OnFailure (flow);
			}
		}
	}
}


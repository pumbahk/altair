using System;
using System.Threading.Tasks;
using QR.message;
using System.Collections.Generic;

namespace QR
{
	/// <summary>
	/// Case QR print for one. 印刷(1枚)
	/// </summary>
	public class CaseQRPrintForOne :AbstractCase,ICase
	{
		public TicketData TicketData { get; set; }

		public CaseQRPrintForOne (IResource resource, TicketData ticketdata) : base (resource)
		{
			TicketData = ticketdata;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintFinish (Resource);
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, List<byte[]>> result = await Resource.QRPrinting.FetchImageAsync (this.TicketData);
                if (result.Status) {
					return true;
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,List<byte[]>>).Result);
					return false;
				}
			} catch (Exception ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnFailure (IFlow flow)
		{
			return new CaseFailureRedirect (Resource);
		}
	}
}


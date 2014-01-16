using System;
using QR.message;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	/// <summary>
	/// Case QR confirm for all. QR表示(all)
	/// </summary>
	// 
	public class CaseQRConfirmForAll: AbstractCase,ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public TicketData TicketData { get; set; }

		public TicketDataCollection TicketDataCollection { get; set; }

		public CaseQRConfirmForAll (IResource resource, TicketData ticketdata) : base (resource)
		{
			TicketData = ticketdata;
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				var data = new TicketDataCollectionRequestData(){order_no = TicketData.order_no, secret = TicketData.secret};
				ResultTuple<string, TicketDataCollection> result = await Resource.TicketDataCollectionFetcher.FetchAsync (data);
				if (result.Status) {
					this.TicketDataCollection = result.Right;
					return true;
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,TicketDataCollection>).Result);
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
			return new CasePrintForAll (Resource, TicketDataCollection);
		}
	}
}


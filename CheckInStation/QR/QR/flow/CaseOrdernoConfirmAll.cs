using System;
using QR.message;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	/// <summary>
	/// Case Orderno confirm for all. Orderno表示(all)
	/// </summary>
	// 
	public class CaseOrdernoConfirmForAll: AbstractCase,ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public OrdernoRequestData RequestData { get; set; }

		public TicketDataCollection Collection { get; set; }

		public CaseOrdernoConfirmForAll (IResource resource, OrdernoRequestData requestData) : base (resource)
		{
			this.RequestData = requestData;
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				var data = new TicketDataCollectionRequestData (){ order_no = this.RequestData.order_no, secret = this.RequestData.secret };
				ResultTuple<string, TicketDataCollection> result = await Resource.TicketDataCollectionFetcher.FetchAsync (data);
				if (result.Status) {
					this.Collection = result.Right;
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
			return new CasePrintForAll (Resource, this.Collection);
		}
	}
}


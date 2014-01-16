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

		public VerifiedOrdernoRequestData RequestData { get; set; }

		public TicketDataCollection Collection { get; set; }

		protected bool fetchStatus;

		public CaseOrdernoConfirmForAll (IResource resource, VerifiedOrdernoRequestData requestData) : base (resource)
		{
			this.RequestData = requestData;
		}

		public override async Task PrepareAsync (IInternalEvent ev)
		{
			await base.PrepareAsync (ev).ConfigureAwait(false);
			try {
				var data = new TicketDataCollectionRequestData () {
					order_no = this.RequestData.order_no,
					secret = this.RequestData.secret
				};
				ResultTuple<string, TicketDataCollection> result = await Resource.TicketDataCollectionFetcher.FetchAsync (data);
				if (result.Status) {
					this.Collection = result.Right;
					this.fetchStatus = true;
				} else {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,TicketDataCollection>).Result);
					this.fetchStatus = false;
				}
			} catch (Exception ex) {
				logger.ErrorException (":", ex);
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				this.fetchStatus = false;
			}
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => this.fetchStatus);
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CasePrintForAll (Resource, this.Collection);
		}
	}
}


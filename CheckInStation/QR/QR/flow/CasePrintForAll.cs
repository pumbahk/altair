using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using QR.message;
using NLog;

namespace QR
{
	/// <summary>
	/// Case QR print for all. 印刷(all)
	/// </summary>
	public class CasePrintForAll :AbstractCase,ICase,IAutoForwardingCase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public TicketDataCollection DataCollection { get; set; }

		public ResultStatusCollector<string> StatusCollector { get; set; }

		public ResultTuple<string, List<TicketImageData>> PrintingTargets;

		public UpdatePrintedAtRequestData RequestData{ get; set; }

		public CasePrintForAll (IResource resource, TicketDataCollection collection) : base (resource)
		{
			DataCollection = collection;
			StatusCollector = new ResultStatusCollector<string> ();
		}

		public override async Task PrepareAsync (IInternalEvent ev)
		{
			await base.PrepareAsync (ev).ConfigureAwait (false);
			var subject = this.PresentationChanel as PrintingEvent;

			try {
				var result = this.PrintingTargets = await Resource.SVGImageFetcher.FetchImageDataForAllAsync (this.DataCollection).ConfigureAwait (false);
				if (result.Status) {
					//印刷枚数設定
					subject.ConfigureByTotalPrinted(result.Right.Count);
				}
			} catch (Exception ex) {
				logger.ErrorException (":", ex);
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
			}
		}

		public override async Task<bool> VerifyAsync ()
		{
			// 印刷対象の画像の取得に失敗した時
			if (!this.PrintingTargets.Status) {
				PresentationChanel.NotifyFlushMessage ((this.PrintingTargets as Failure<string,List<TicketImageData>>).Result);
				return false;
			}
			var subject = this.PresentationChanel as PrintingEvent;
            subject.ChangeState(PrintingStatus.printing);

			try {
				var printing = Resource.TicketImagePrinting;
				foreach (var imgdata in this.PrintingTargets.Right) {
					var status = await printing.EnqueuePrinting (imgdata).ConfigureAwait (false);
					subject.PrintFinished(); //印刷枚数インクリメント
					StatusCollector.Add (imgdata.token_id, status);
				}

				this.RequestData = new UpdatePrintedAtRequestData () {
					token_id_list = StatusCollector.Result ().SuccessList.ToArray (),
					secret = this.DataCollection.secret,
					order_no = this.DataCollection.additional.order.order_no
				};
                subject.ChangeState(PrintingStatus.finished);
				return StatusCollector.Status;
			} catch (Exception ex) {
				logger.ErrorException (":", ex);
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CasePrintFinish (this.Resource, this.RequestData);
		}

		public override ICase OnFailure (IFlow flow)
		{
			flow.Finish ();
			Func<Task<bool>> modify = (async () => {
				if (this.RequestData != null) {
					IEnumerable<string> used = StatusCollector.Result ().SuccessList;
					foreach (var k in used) {
						logger.Warn ("{0} is printed. but all status is failure", k);
					}
					await Resource.TicketDataManager.UpdatePrintedAtAsync (this.RequestData);
				}
				return true;
			});
			return new CaseFailureRedirect (Resource, modify);
		}
	}
}


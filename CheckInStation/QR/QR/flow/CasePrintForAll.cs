using System;
using System.Collections.Generic;
using System.Threading.Tasks;
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

		public CasePrintForAll (IResource resource, TicketDataCollection collection) : base (resource)
		{
			DataCollection = collection;
			StatusCollector = new ResultStatusCollector<string> ();
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, List<TicketImageData>> result = await Resource.SVGImageFetcher.FetchImageDataForAllAsync(this.DataCollection).ConfigureAwait(false);
				if (!result.Status) {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,List<TicketImageData>>).Result);
					return false;
				}

				var printing = Resource.TicketImagePrinting;
				foreach (var imgdata in result.Right) {
					var status = await printing.EnqueuePrinting (imgdata).ConfigureAwait(false);
					StatusCollector.Add (imgdata.token_id, status);
				}
				return StatusCollector.Status;
			} catch (Exception ex) {
				logger.ErrorException (":", ex);
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CasePrintFinish (this.Resource, StatusCollector);
		}

		public override ICase OnFailure (IFlow flow)
		{
			flow.Finish ();
			Func<Task<bool>> modify = (async () => {
				IEnumerable<string> used = StatusCollector.Result ().SuccessList;
				foreach (var k in used) {
					//TODO:LOG
					Console.WriteLine ("{0} is printed. but all status is failure", k);
				}
				return await Resource.TicketDataManager.UpdatePrintedAtAsync (used);
			});
			return new CaseFailureRedirect (Resource, modify);
		}
	}
}


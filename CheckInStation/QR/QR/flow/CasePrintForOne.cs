using System;
using System.Threading.Tasks;
using QR.message;
using System.Collections.Generic;
using NLog;

namespace QR
{
	/// <summary>
	/// Case QR print for one. 印刷(1枚)
	/// </summary>
	public class CasePrintForOne :AbstractCase,ICase
	{
		public TicketData TicketData { get; set; }

		public ResultStatusCollector<string> StatusCollector { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public CasePrintForOne (IResource resource, TicketData ticketdata) : base (resource)
		{
			TicketData = ticketdata;
			StatusCollector = new ResultStatusCollector<string> ();
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, List<TicketImageData>> result = await Resource.SVGImageFetcher.FetchImageDataForOneAsync (this.TicketData).ConfigureAwait(false);
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
			Func<Task<bool>> modify = (async () => {
				IEnumerable<string> used = StatusCollector.Result ().SuccessList;
				foreach (var k in used) {
					logger.Error ("{0} is printed. but summalized status is failure", k);
				}
				return await Resource.TicketDataManager.UpdatePrintedAtAsync (used);
			});
			return new CaseFailureRedirect (Resource, modify);
		}
	}
}


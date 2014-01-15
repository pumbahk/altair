using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case QR print for all. 印刷(all)
	/// </summary>
	public class CaseQRPrintForAll :AbstractCase,ICase
	{
		public TicketData TicketData { get; set; }

		public ResultStatusCollector<string> StatusCollector { get; set; }

		public CaseQRPrintForAll (IResource resource, TicketData ticketdata) : base (resource)
		{
			TicketData = ticketdata;
			StatusCollector = new ResultStatusCollector<string> ();
		}

		public override async Task<bool> VerifyAsync ()
		{
			try {
				ResultTuple<string, List<byte[]>> result = await Resource.SVGImageFetcher.FetchImageForOneAsync (this.TicketData);
				if (!result.Status) {
					//modelからpresentation層へのメッセージ
					PresentationChanel.NotifyFlushMessage ((result as Failure<string,List<byte[]>>).Result);
					return false;
				}

				var printing = Resource.TicketImagePrinting;
				foreach (var img in result.Right) {
					var status = await printing.EnqueuePrinting (img);
					StatusCollector.Add (TicketData.ordered_product_item_token_id, status);
				}
				return StatusCollector.Status;
			} catch (Exception ex) {
				PresentationChanel.NotifyFlushMessage (ex.ToString ());
				PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintFinish (this.Resource, StatusCollector);
		}

		public override ICase OnFailure (IFlow flow)
		{
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


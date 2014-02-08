using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using QR.message;
using NLog;
using System.Net;

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

            try
            {
                var result = this.PrintingTargets = await Resource.SVGImageFetcher.FetchImageDataForAllAsync(this.DataCollection).ConfigureAwait(false);
                if (result.Status)
                {
                    //印刷枚数設定
                    subject.ConfigureByTotalPrinted(result.Right.Count);
                }
                else
                {
                    subject.ConfigureByTotalPrinted(0); //失敗時;
                }
            }
            catch (WebException ex)
            {
                logger.ErrorException(":", ex);
                this.PrintingTargets = new Failure<string, List<TicketImageData>>(Resource.GetWebExceptionMessage());
            }
            catch (Exception ex)
            {
                logger.ErrorException(":", ex);
                this.PrintingTargets = new Failure<string, List<TicketImageData>>(Resource.GetDefaultErrorMessage());
            }
		}
				
		public override async Task<bool> VerifyAsync ()
        {	
			// 印刷対象の画像の取得に失敗した時
			if (!this.PrintingTargets.Status) {
                PresentationChanel.NotifyFlushMessage(this.PrintingTargets.Left);
				PresentationChanel.NotifyFlushMessage ((this.PrintingTargets as Failure<string,List<TicketImageData>>).Result);
				return false;
			}
			var subject = this.PresentationChanel as PrintingEvent;
            subject.ChangeState(PrintingStatus.printing);

            var printing = Resource.TicketPrinting;
			try {
                printing.BeginEnqueue();
				foreach (var imgdata in this.PrintingTargets.Right) {
                    var status = await printing.EnqueuePrinting(imgdata, subject).ConfigureAwait(true);
					subject.PrintFinished(); //印刷枚数インクリメント
					StatusCollector.Add (imgdata.token_id, status);
				}
                printing.EndEnqueue();

				this.RequestData = new UpdatePrintedAtRequestData () {
					token_id_list = StatusCollector.Result ().SuccessList.ToArray (),
					secret = this.DataCollection.secret,
					order_no = this.DataCollection.additional.order.order_no
				};
                subject.ChangeState(PrintingStatus.finished);
				return StatusCollector.Status;
			} catch (Exception ex) {
                if (printing != null)
                    printing.EndEnqueue();

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

            if (this.PrintingTargets != null)
            {
                return new CaseFailureRedirect(Resource, modify, this.PrintingTargets.Left);
            }
            else
            {
                return new CaseFailureRedirect(Resource, modify);
            }
		}
	}
}


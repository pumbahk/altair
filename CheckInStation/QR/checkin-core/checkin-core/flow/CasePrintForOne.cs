using System;
using System.Threading.Tasks;
using checkin.core.message;
using System.Collections.Generic;
using NLog;
using System.Linq;
using System.Net;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{

    /// <summary>
    /// Case QR print for one. 印刷(1枚)
    /// </summary>
    public class CasePrintForOne :AbstractCase,ICase,IAutoForwardingCase
    {
        public TicketData TicketData { get; set; }

        public ResultTuple<string, List<TicketImageData>> PrintingTargets { get; set; }

        public AggregateTicketPrinting AggregateTicketPrinting { get; set; }

        public UpdatePrintedAtRequestData RequestData{ get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public CasePrintForOne (IResource resource, TicketData ticketdata) : base (resource)
        {
            TicketData = ticketdata;
            this.AggregateTicketPrinting = new AggregateTicketPrinting(resource.TicketPrinting);
        }

        public override async Task PrepareAsync(IInternalEvent ev)
        {
            await base.PrepareAsync(ev).ConfigureAwait(false);
            var subject = this.PresentationChanel as PrintingEvent;
            var d = new DispatchResponse<List<TicketImageData>>(this.Resource);
            var result = this.PrintingTargets = await d.Dispatch(() => Resource.SVGImageFetcher.FetchImageDataForOneAsync(this.TicketData)).ConfigureAwait(false);
            if (result.Status)
            {
                subject.ConfigureByTotalPrinted(result.Right.Count); //印刷枚数設定
            }
            else
            {
                this.PresentationChanel.NotifyFlushMessage(result.Left);
                subject.ConfigureByTotalPrinted(0); //失敗時;
            }
        }

        public override Task<bool> VerifyAsync ()
        {
            var ts = new TaskCompletionSource<bool>();
            // 印刷対象の画像の取得に失敗した時
            if (!this.PrintingTargets.Status) {
                ts.SetResult(false);
                PresentationChanel.NotifyFlushMessage(this.PrintingTargets.Left);
                return ts.Task;
            }

            // 印刷開始
            var subject = this.PresentationChanel as PrintingEvent;
            subject.ChangeState(PrintingStatus.printing);
            try
            {
                this.AggregateTicketPrinting.Act(subject, this.PrintingTargets.Right, (this.PresentationChanel as PrintingEvent).StatusInfo.TotalPrinted);
                this.RequestData = UpdatePrintedAtRequestData.Build(this.TicketData, this.AggregateTicketPrinting.SuccessList);

                var s = this.AggregateTicketPrinting.Status;
                ts.SetResult(s);
                if (!s)
                {
                    PresentationChanel.NotifyFlushMessage(MessageResourceUtil.GetLoginFailureMessageFormat(Resource));
                }
            }
            catch (TransparentMessageException ex)
            {
                PresentationChanel.NotifyFlushMessage(ex.Message);
                this.PrintingTargets.Left = ex.Message;
                ts.SetResult(false);
            }
            return ts.Task;
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
                    foreach (var p in this.RequestData.printed_ticket_list)
                    {
                        logger.Warn("token_id={0}, template_id={1} is printed. but all status is failure".WithMachineName(), p.token_id,p.template_id);
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


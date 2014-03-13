using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using QR.message;
using NLog;
using System.Net;
using QR.support;

namespace QR
{
    /// <summary>
    /// Case QR print for all. 印刷(all)
    /// </summary>
    public class CasePrintForAll :AbstractCase,ICase,IAutoForwardingCase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketDataCollection DataCollection { get; set; }

        public AggregateTicketPrinting AggregateTicketPrinting { get; set; }

        public ResultTuple<string, List<TicketImageData>> PrintingTargets;

        public UpdatePrintedAtRequestData RequestData{ get; set; }

        public CasePrintForAll (IResource resource, TicketDataCollection collection) : base (resource)
        {
            DataCollection = collection;
            this.AggregateTicketPrinting = new AggregateTicketPrinting(this.Resource.TicketPrinting);
        }

        public override async Task PrepareAsync(IInternalEvent ev)
        {
            await base.PrepareAsync(ev).ConfigureAwait(false);
            var subject = this.PresentationChanel as PrintingEvent;
            {
                var result = this.PrintingTargets = await new DispatchResponse<List<TicketImageData>>(Resource).Dispatch(() => Resource.SVGImageFetcher.FetchImageDataForAllAsync(this.DataCollection)).ConfigureAwait(false);

                if (result.Status)
                {
                    //印刷枚数設定
                    subject.ConfigureByTotalPrinted(result.Right.Count);
                }
                else
                {
                    this.PresentationChanel.NotifyFlushMessage(result.Left);
                    subject.ConfigureByTotalPrinted(0); //失敗時;
                }            
            }
        }
                
        public override async Task<bool> VerifyAsync ()
        {
            // 印刷対象の画像の取得に失敗した時
            if (!this.PrintingTargets.Status)
            {
                PresentationChanel.NotifyFlushMessage(this.PrintingTargets.Left);
                return false;
            }

            // 印刷開始
            var subject = this.PresentationChanel as PrintingEvent;
            subject.ChangeState(PrintingStatus.printing);

            await this.AggregateTicketPrinting.Act(subject, this.PrintingTargets.Right);
            this.RequestData = UpdatePrintedAtRequestData.Build(this.DataCollection, this.AggregateTicketPrinting.SuccessList);

            var s = this.AggregateTicketPrinting.Status;
            if (!s)
            {
                PresentationChanel.NotifyFlushMessage(MessageResourceUtil.GetLoginFailureMessageFormat(Resource));
            }
            return s;
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
                        logger.Warn("token_id={0}, template_id={1} is printed. but all status is failure".WithMachineName(), p.token_id, p.template_id);
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


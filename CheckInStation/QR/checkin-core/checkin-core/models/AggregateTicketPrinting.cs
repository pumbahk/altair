using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.models
{
    using TokenTicketTemplatePairCollector = ResultStatusCollector<Tuple<string, string>>;
    using TokenTicketTemplatePair = Tuple<string, string>;
using NLog;

    public class AggregateTicketPrinting
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

        private PrintingEvent subject;

        private TokenTicketTemplatePairCollector pushedRequestCollector;

        private ITicketPrinting printing;


        public AggregateTicketPrinting(ITicketPrinting printing)
        {
            this.printing = printing;
            this.pushedRequestCollector = new TokenTicketTemplatePairCollector();
        }

        public void Act(PrintingEvent subject, IEnumerable<TicketImageData> source, int expectedTotalPrinted)
        {
            this.printing.BeginEnqueue();
            var actualTotalPrinted = 0;
            foreach (var imgdata in source)
            {
                try
                {
                    var status = printing.EnqueuePrinting(imgdata, subject);
                    subject.PrintFinished(); //印刷枚数インクリメント
                    actualTotalPrinted += 1;
                    this.pushedRequestCollector.Add(Tuple.Create(imgdata.token_id, imgdata.ticket_id), status);
                }
                catch (Exception ex)
                {
                    logger.WarnException("".WithMachineName(), ex);
                    this.pushedRequestCollector.Add(Tuple.Create(imgdata.token_id, imgdata.ticket_id), false);
                }
            }
            if (actualTotalPrinted != expectedTotalPrinted) //xxx:
            {
                logger.Error("ticket printing: expected ={0}, but printed ={1}", expectedTotalPrinted, actualTotalPrinted);
                throw new TransparentMessageException("発券された枚数に間違いがあります");
            }
            subject.StatusInfo.Status = PrintingStatus.finished;
            this.printing.EndEnqueue();
        }

        public IEnumerable<TokenTicketTemplatePair> SuccessList
        {
            get { return this.pushedRequestCollector.Result().SuccessList; }
        }

        public bool Status
        {
            get { return this.pushedRequestCollector.Status; }
        }
    }
}

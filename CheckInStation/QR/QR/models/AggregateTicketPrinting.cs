using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using QR.support;

namespace QR
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

        public async Task Act(PrintingEvent subject, IEnumerable<TicketImageData> source)
        {
            this.printing.BeginEnqueue();
            foreach (var imgdata in source)
            {
                try
                {
                    var status = await printing.EnqueuePrinting(imgdata, subject).ConfigureAwait(true);
                    subject.PrintFinished(); //印刷枚数インクリメント
                    this.pushedRequestCollector.Add(Tuple.Create(imgdata.token_id, imgdata.ticket_id), status);
                }
                catch (Exception ex)
                {
                    logger.WarnException("".WithMachineName(), ex);
                    this.pushedRequestCollector.Add(Tuple.Create(imgdata.token_id, imgdata.ticket_id), false);
                }
            }
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

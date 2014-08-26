using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core.message;

namespace checkin.core.flow
{
    /// <summary>
    /// Case QR confirm for one. QR表示(1枚)
    /// </summary>
    public class CaseQRConfirmForOne : AbstractCase, ICase
    {
        public PrintUnit Unit { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public TicketData TicketData { get; set; }

        public CaseQRConfirmForOne (IResource resource, TicketData ticketdata) : base (resource)
        {
            Unit = PrintUnit.one;
            TicketData = ticketdata;
        }
        public override Task PrepareAsync(IInternalEvent ev)
        {
            var subject = ev as ConfirmOneEvent;
            subject.SetData(this.TicketData);
            return base.PrepareAsync(ev);
        }
        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                var subject = PresentationChanel as ConfirmOneEvent;
                PrintUnit unit;
                var status = EnumUtil.TryParseEnum<PrintUnit> (subject.PrintUnitString, out unit);
                subject.PrintUnit = Unit = unit;
                return status;
            });
        }

        public override ICase OnSuccess (IFlow flow)
        {
            switch (Unit) {
            case PrintUnit.one:
                return new CasePrintForOne (Resource, TicketData);
            case PrintUnit.all:
                return new CaseQRConfirmForAll (Resource, TicketData);
            default:
                logger.Info ("PrintUnit: {0} is unknown value. default={1} is selected".WithMachineName(), Unit.ToString(), default(PrintUnit));
                return new CasePrintForOne (Resource, TicketData);
            }
        }
    }
}


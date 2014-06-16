using System;

namespace checkin.core.events
{
    public enum PrintingStatus
    {
        starting,
        prepared,
        requesting,
        printing,
        finished
    }

    public interface IPrintingStatusInfo
    {
        PrintingStatus Status { get; set; }

        int FinishedPrinted { get; set; }

        int TotalPrinted { get; set; }
    }

    public class PrintingEvent : AbstractEvent, IInternalEvent
    {
        public IPrintingStatusInfo StatusInfo;

        public void ConfigureByTotalPrinted (int numOfPirnted)
        {
            var s = this.StatusInfo;
            s.Status = PrintingStatus.prepared;
            s.TotalPrinted = numOfPirnted;
            s.FinishedPrinted = 0;
        }

        public void ChangeState (PrintingStatus s)
        {
            this.StatusInfo.Status = s;
        }

        public void PrintFinished ()
        {
            this.StatusInfo.FinishedPrinted += 1;
        }
    }
}


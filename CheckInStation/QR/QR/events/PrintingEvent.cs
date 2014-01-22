using System;

namespace QR
{
	public enum PrintingStatus
	{
		starting,
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
			s.Status = PrintingStatus.requesting;
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


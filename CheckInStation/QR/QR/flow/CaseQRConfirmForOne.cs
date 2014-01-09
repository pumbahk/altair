using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case QR confirm for one. QR表示(1枚)
	/// </summary>
	public class CaseQRConfirmForOne : AbstractCase, ICase
	{
		public PrintUnit Unit { get; set; }

		public TicketData TicketData { get; set; }

		public CaseQRConfirmForOne (IResource resource, TicketData ticketdata) : base (resource)
		{
			Unit = PrintUnit.one;
			TicketData = ticketdata;
		}

		public override Task ConfigureAsync (IInternalEvent ev)
		{
			return Task.Run (() => {
				var subject = ev as QRInputEvent;
				PrintUnit unit;
				var status = subject.TryParseEnum (subject.PrintUnitString, out unit);
				if (status)
					Unit = subject.PrintUnit = unit; 
			});
		}

		public override ICase OnSuccess (IFlow flow)
		{
			switch (Unit) {
			case PrintUnit.one:
				return new CaseQRPrintForOne (Resource, TicketData);
			case PrintUnit.all:
				return new CaseQRConfirmForAll (Resource);
			default:
				throw new NotImplementedException ();
			}
		}
	}
}


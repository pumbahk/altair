using System;

namespace QR
{
	/// <summary>
	/// Case QR confirm for all. QR表示(all)
	/// </summary>
	public class CaseQRConfirmForAll: AbstractCase,ICase
	{
		public TicketData TicketData { get; set; }

		public CaseQRConfirmForAll (IResource resource, TicketData ticketdata) : base (resource)
		{
			TicketData = ticketdata;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintForAll (Resource,TicketData);
		}
	}
}


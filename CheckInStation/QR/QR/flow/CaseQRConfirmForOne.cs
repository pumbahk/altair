using System;

namespace QR
{
	public class CaseQRConfirmForOne : AbstractCase, ICase
	{
		public PrintUnit Unit { get; set; }

		public CaseQRConfirmForOne (IResource resource) : base (resource)
		{
			Unit = PrintUnit.one;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			switch (Unit) {
			case PrintUnit.one:
				return new CaseQRPrintForOne (Resource);
			case PrintUnit.all:
				return new CaseQRConfirmForAll (Resource);
			default:
				throw new NotImplementedException ();
			}
		}
	}
}


using System;

namespace QR
{
	public class CaseQRConfirmForAll: AbstractCase,ICase
	{
		public CaseQRConfirmForAll (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintForAll (Resource);
		}
	}
}


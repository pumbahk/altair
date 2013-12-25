using System;

namespace QR
{
	public class CaseQRPrintForAll :AbstractCase,ICase
	{
		public CaseQRPrintForAll (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			throw new NotImplementedException ();
		}
	}
}


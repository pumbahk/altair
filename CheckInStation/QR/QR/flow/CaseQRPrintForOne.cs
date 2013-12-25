using System;

namespace QR
{
	public class CaseQRPrintForOne :AbstractCase,ICase
	{
		public CaseQRPrintForOne (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintFinish (Resource);
		}
	}
}


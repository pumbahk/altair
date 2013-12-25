using System;

namespace QR
{
	/// <summary>
	/// Case QR print for all. 印刷(all)
	/// </summary>
	public class CaseQRPrintForAll :AbstractCase,ICase
	{
		public CaseQRPrintForAll (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintFinish (Resource);
		}

		public override ICase OnFailure (IFlow flow)
		{
			return new CaseFailureRedirect (Resource);
		}
	}
}


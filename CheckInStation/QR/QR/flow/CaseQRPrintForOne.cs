using System;

namespace QR
{
	/// <summary>
	/// Case QR print for one. 印刷(1枚)
	/// </summary>
	public class CaseQRPrintForOne :AbstractCase,ICase
	{
		public CaseQRPrintForOne (IResource resource) : base (resource)
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


using System;

namespace QR
{
	/// <summary>
	/// Case QR confirm for all. QR表示(all)
	/// </summary>
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


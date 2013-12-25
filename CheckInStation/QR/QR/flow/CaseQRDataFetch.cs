using System;

namespace QR
{
	public class CaseQRDataFetch : AbstractCase, ICase
	{
		public CaseQRDataFetch (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRConfirmForOne (Resource);
		}
	}
}


using System;

namespace QR
{
	public class CaseQRCodeInput :AbstractCase, ICase
	{
		public CaseQRCodeInput (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRDataFetch (Resource);
		}
	}

	public enum PrintUnit
	{
		one,
		all
	}
}


using System;

namespace QR
{

	/// <summary>
	/// Case QR data fetch. QRからデータ取得中
	/// </summary>
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


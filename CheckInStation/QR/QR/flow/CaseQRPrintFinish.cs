using System;

namespace QR
{
	/// <summary>
	/// Case QR print finish. 発券しました
	/// </summary>
	public class CaseQRPrintFinish: AbstractCase,ICase
	{
		public CaseQRPrintFinish (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			flow.Finish ();
			return new CaseQRCodeInput (Resource); // TODO: ここトップに戻るが良いんだろうか
		}
	}
}


using System;

namespace QR
{
	/// <summary>
	/// Case qr input select. 認証方法選択画面
	/// </summary>
	public class CaseQRInputStrategySelect :AbstractCase, ICase
	{
		public CaseQRInputStrategySelect (IResource resource) : base(resource)
		{
		}

		public override ICase OnSuccess(IFlow flow){
			return flow.GetFlowDefinition().StartPointCase(this);
		}
	}
}

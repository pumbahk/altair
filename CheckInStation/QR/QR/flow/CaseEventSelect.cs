using System;

namespace QR
{
	/// <summary>
	/// Case event select. イベント一覧画面
	/// </summary>
	public class CaseEventSelect :AbstractCase, ICase
	{
		public CaseEventSelect (IResource resource) : base(resource)
		{
		}

		public override ICase OnSuccess(IFlow flow){
			return flow.GetFlowDefinition().StartPointCase(this);
		}
	}
}


using System;

namespace QR
{
	/// <summary>
	/// Case failure redirect. エラー表示。 キャンセル済みなど予期しない状況の時にリダイレクトメッセージ表示する状況
	/// </summary>
	public class CaseFailureRedirect : AbstractCase, ICase
	{
		public CaseFailureRedirect (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			IFlowDefinition def = flow.GetFlowDefinition();
			return def.StartPointCase (this);
		}
	}
}


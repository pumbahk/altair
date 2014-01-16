using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case failure redirect. エラー表示。 キャンセル済みなど予期しない状況の時にリダイレクトメッセージ表示する状況
	/// </summary>
	public class CaseFailureRedirect : AbstractCase, ICase
	{
		public Func<Task> Modify { get; set; }

		public CaseFailureRedirect (IResource resource) : base (resource)
		{
		}

		public CaseFailureRedirect (IResource resource, Func<Task> modify) : base (resource)
		{
			this.Modify = modify;
		}

		public override async Task<bool> VerifyAsync()
		{
			if(this.Modify != null){
				await this.Modify();
			}
			return true;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			IFlowDefinition def = flow.GetFlowDefinition ();
			return def.AfterFailureRedirect (this);
		}
	}
}


using System;

namespace QR
{
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


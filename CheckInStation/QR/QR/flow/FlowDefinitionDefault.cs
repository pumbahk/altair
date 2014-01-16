using System;

namespace QR
{
	public class FlowDefinitionDefault : IFlowDefinition
	{
		public ICase AfterFailureRedirect (ICase case_)
		{
			return AfterFailureRedirect (case_.Resource);
		}

		public ICase AfterFailureRedirect (IResource resource)
		{
			return new CaseQRCodeInput (resource);
		}

		public ICase AfterAuthorization (IResource resource)
		{
			return new CaseInputStrategySelect (resource);
		}

		public ICase AfterPrintFinish (IResource resource)
		{
			return new CaseQRCodeInput (resource);
		}
	}
}


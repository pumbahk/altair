using System;

namespace QR
{
	public class FlowDefinitionDefault : IFlowDefinition
	{
		public ICase StartPointCase (ICase case_)
		{
			return StartPointCase (case_.Resource);
		}

		public ICase StartPointCase (IResource resource)
		{
			return new CaseQRCodeInput (resource);
		}
	}
}


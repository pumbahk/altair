using System;

namespace QR
{
	public interface IFlowDefinition
	{
		ICase StartPointCase(ICase case_);
		ICase StartPointCase(IResource resource);
	}
}


using System;

namespace QR
{
	public interface IFlowDefinition
	{
		ICase AfterFailureRedirect(ICase case_);
		ICase AfterFailureRedirect(IResource resource);

		ICase AfterPrintFinish(IResource resource);
		ICase AfterAuthorization(IResource resource);
	}
}


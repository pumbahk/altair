using System;

namespace QR
{
	public interface IFlowDefinition
	{

        InputUnit CurrentInputUnit { get; set; }

		ICase AfterFailureRedirect(IResource resource);

		ICase AfterPrintFinish(IResource resource);
		ICase AfterAuthorization(IResource resource);
		ICase AfterSelectInputStrategy (IResource resource, InputUnit Selected);
		ICase AfterQRDataFetch(IResource resource, TicketData tdata);

		ICase PreviousCaseFromRedirected(IResource resource);
	}
}


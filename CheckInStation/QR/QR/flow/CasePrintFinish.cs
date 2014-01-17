using System;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace QR
{
	/// <summary>
	/// Case QR print finish. 発券しました
	/// </summary>
	public class CasePrintFinish: AbstractCase,ICase,IAutoForwardingCase
	{
		public UpdatePrintedAtRequestData RequsetData { get; set; }

		public CasePrintFinish (IResource resource, UpdatePrintedAtRequestData data) : base (resource)
		{
			this.RequsetData = data;
		}

		public override async Task<bool> VerifyAsync ()
		{	
			return await Resource.TicketDataManager.UpdatePrintedAtAsync (this.RequsetData);
		}

		public override ICase OnSuccess (IFlow flow)
		{
			flow.Finish ();
			return flow.GetFlowDefinition ().AfterPrintFinish (Resource);
		}
	}
}


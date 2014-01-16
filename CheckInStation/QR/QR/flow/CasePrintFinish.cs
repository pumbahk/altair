using System;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace QR
{
	/// <summary>
	/// Case QR print finish. 発券しました
	/// </summary>
	public class CasePrintFinish: AbstractCase,ICase
	{
		public ResultStatusCollector<string> StatusCollector { get; set; }

		public CasePrintFinish (IResource resource, ResultStatusCollector<string> statusCollector) : base (resource)
		{
			StatusCollector = statusCollector;
		}

		public override async Task<bool> VerifyAsync ()
		{	
			IEnumerable<string> used = StatusCollector.Result ().SuccessList;
			return await Resource.TicketDataManager.UpdatePrintedAtAsync (used);
		}

		public override ICase OnSuccess (IFlow flow)
		{
			flow.Finish ();
			return flow.GetFlowDefinition ().AfterPrintFinish (Resource);
		}
	}
}


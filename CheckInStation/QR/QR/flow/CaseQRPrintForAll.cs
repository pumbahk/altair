using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case QR print for all. 印刷(all)
	/// </summary>
	public class CaseQRPrintForAll :AbstractCase,ICase
	{
		public TicketData TicketData { get; set; }

		public ResultStatusCollector<string> StatusCollector { get; set; }

		public CaseQRPrintForAll (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintFinish (this.Resource, StatusCollector);
		}

		public override ICase OnFailure (IFlow flow)
		{
			Func<Task<bool>> modify = (async () => {
				IEnumerable<string> used = StatusCollector.Result ().SuccessList;
				foreach (var k in used) {
					//TODO:LOG
					Console.WriteLine ("{0} is printed. but all status is failure", k);
				}
				return await Resource.TicketDataManager.UpdatePrintedAtAsync (used);
			});
			return new CaseFailureRedirect (Resource, modify);
		}
	}
}


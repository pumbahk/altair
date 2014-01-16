using System;
using System.Threading.Tasks;
using NLog;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case CaseOrdernoDataFetch. 
	/// </summary>
	public class CaseOrdernoVerifyRequestData : AbstractCase, ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public OrdernoRequestData RequestData { get; set; }

		public TicketDataCollection Collection { get; set; }

		public CaseOrdernoVerifyRequestData (IResource resource, OrdernoRequestData data) : base (resource)
		{
			this.RequestData = data;
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseOrdernoConfirmForAll (this.Resource, this.RequestData);
		}
	}
}


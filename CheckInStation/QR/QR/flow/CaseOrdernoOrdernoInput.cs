using System;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	/// <summary>
	/// Case CaseOrdernoOrdernoInput. 
	/// </summary>
	public class CaseOrdernoOrdernoInput : AbstractCase, ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public OrdernoRequestData RequestData { get; set; }

		public CaseOrdernoOrdernoInput (IResource resource) : base (resource)
		{
			this.RequestData = new OrdernoRequestData ();
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
                var subject = this.PresentationChanel as OrdernoInputEvent;
                this.RequestData.order_no = subject.Orderno;
				return this.RequestData.order_no != null;
			});
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseOrdernoTelInput(Resource, RequestData);
		}

		public override ICase OnFailure (IFlow flow)
		{
			PresentationChanel.NotifyFlushMessage ("failure");
			return this;
		}
	}
}

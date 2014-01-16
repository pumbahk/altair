using System;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	/// <summary>
	/// Case CaseOrdernoTelInput. 
	/// </summary>
	public class CaseOrdernoTelInput : AbstractCase, ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public OrdernoRequestData RequestData { get; set; }

		public CaseOrdernoTelInput (IResource resource, OrdernoRequestData data) : base (resource)
		{
			this.RequestData = data;
		}

		public override Task ConfigureAsync (IInternalEvent ev)
		{
			OrdernoInputEvent subject  = ev as OrdernoInputEvent;
			this.RequestData.tel = subject.Tel;
			return base.ConfigureAsync(ev);
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				return this.RequestData.tel != null;
			});
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseOrdernoVerifyRequestData (this.Resource, this.RequestData);
		}
	}
}

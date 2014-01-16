using System;
using System.Threading.Tasks;

namespace QR
{
	class FakeFlow : Flow
	{
		public FakeFlow (FlowManager manager, ICase _case) : base (manager, _case)
		{
		}

		public bool VerifyStatus{ get; set; }

		public override Task PrepareAsync ()
		{
			//ここでは詳細に触れない。
			return Task.Run (() => {
			});
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				return VerifyStatus;
			});
		}

		public override async Task<IFlow> Forward ()
		{
			var nextCase = await NextCase ();
			return new FakeFlow (Manager, nextCase);
		}
	}
}


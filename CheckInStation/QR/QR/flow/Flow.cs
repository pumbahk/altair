using System;
using System.Threading.Tasks;

namespace QR
{
	public enum FlowState
	{
		starting,
		running,
		ending
	}

	public class Flow : IFlow
	{
		public ICase Case { get; set; }
		//		public FlowState State { get; set; }
		public FlowManager Manager { get; set; }

		public virtual async Task<bool> VerifyAsync ()
		{
			var status = await Case.VerifyAsync ();
			var evStatus = status ? InternalEventStaus.success : InternalEventStaus.failure;
			Manager.GetInternalEvent ().Status = evStatus;
			return status;
		}

		public virtual Task PrepareAsync ()
		{
			return Case.PrepareAsync (Manager.GetInternalEvent ());
		}

		public Flow (FlowManager manager, ICase _case)
		{
			Manager = manager;
			Case = _case;
		}

		public IFlowDefinition GetFlowDefinition ()
		{
			return Manager.FlowDefinition;
		}

		public async Task<ICase> NextCase ()
		{
			await PrepareAsync (); //ここでUIから情報を取得できるようにする必要がある。
			if (await VerifyAsync ()) {
				return Case.OnSuccess (this);
			} else {
				return Case.OnFailure (this);
			}
		}

		public virtual async Task<IFlow> Forward ()
		{
			var nextCase = await NextCase ();
			if (Case == nextCase) {
				return this;
			}
			return new Flow (Manager, nextCase);
		}

		public Task<IFlow> Backward ()
		{
			//XXX:
			return Task.Run<IFlow> (() => {
				return this;
			});
		}

		public bool IsAutoForwarding ()
		{
			return this.Case is IAutoForwardingCase;
		}

		public void Finish ()
		{
			if (!Manager.OnFinish (this)) {
				throw new Exception ("anything is wrong!");
			}
			// 印刷終了後に戻った場合には、認証方法選択画面に遷移
			this.Manager.Push (new Flow (this.Manager, this.GetFlowDefinition ().PreviousCaseFromRedirected (this.Case.Resource)));
		}
	}
}


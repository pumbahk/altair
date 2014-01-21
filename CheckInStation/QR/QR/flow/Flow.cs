using NLog;
using System;
using System.Threading.Tasks;

namespace QR
{
	public enum FlowState
	{
		initialized,
		prepared,
		verified
	}

	public class Flow : IFlow
	{
		public ICase Case { get; set; }

		public FlowManager Manager { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger();
		protected FlowState state;
		protected bool verifyResult;

		public Flow (FlowManager manager, ICase _case)
		{
			this.Manager = manager;
			this.Case = _case;
			this.state = FlowState.initialized;
		}

		private void ChangeState (FlowState s)
		{
			this.state = s;
		}

		public virtual async Task<bool> VerifyAsync ()
		{
            //prepare if not then calling.
            if (this.state < FlowState.prepared)
            {
                await PrepareAsync().ConfigureAwait(false);
            }

			var status = await Case.VerifyAsync ();
			var evStatus = status ? InternalEventStaus.success : InternalEventStaus.failure;
			Manager.GetInternalEvent ().Status = evStatus;

			this.ChangeState (FlowState.verified);
			this.verifyResult = status;
			return status;
		}

		public virtual Task PrepareAsync ()
		{
			var r = Case.PrepareAsync (Manager.GetInternalEvent ());
			this.ChangeState (FlowState.prepared);
			return r;
		}

		public IFlowDefinition GetFlowDefinition ()
		{
			return Manager.FlowDefinition;
		}

		public async Task<ICase> NextCase ()
		{
            logger.Debug(String.Format("FlowState: {0}", this.state));
			//verify if not then calling.
			bool isVerifySuccess;
			if (this.state < FlowState.verified) {
				isVerifySuccess = await VerifyAsync ().ConfigureAwait (false);
			} else {
				isVerifySuccess = this.verifyResult;
			}

			//dispatch by verify status
			if (isVerifySuccess) {
				return Case.OnSuccess (this);
			} else {
				return Case.OnFailure (this);
			}
		}

		public virtual async Task<IFlow> Forward ()
		{
			var nextCase = await NextCase ().ConfigureAwait (false);
			if (Case == nextCase) {
                this.ChangeState(FlowState.prepared);
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
			// 印刷終了後に戻った場合には、認証方法選択画面に遷移するように履歴を調整
			this.Manager.Push (new Flow (this.Manager, this.GetFlowDefinition ().PreviousCaseFromRedirected (this.Case.Resource)));
		}
	}
}


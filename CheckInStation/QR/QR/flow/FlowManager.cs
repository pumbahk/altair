using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	public class FlowManager
	{
		private Stack<IFlow> undoStack;
		private static Logger logger = LogManager.GetCurrentClassLogger ();
		//TODO:rename
		public IFlowDefinition FlowDefinition{ get; set; }

		public RequestBroker RequestBroker{ get; set; }

		public FlowManager (IFlowDefinition def)
		{
			FlowDefinition = def;
			undoStack = new Stack<IFlow> ();
		}

		public FlowManager ()
		{
			FlowDefinition = new FlowDefinitionDefault ();
			undoStack = new Stack<IFlow> ();
		}

		public IInternalEvent GetInternalEvent ()
		{
			if (this.RequestBroker == null) {
                logger.Warn("RequestBroker hasn't Internal Event.");
				return new EmptyEvent ();
			}
			return this.RequestBroker.GetInternalEvent ();	
		}

		public IFlow Peek ()
		{
			return this.undoStack.Peek ();
		}

		public void Push (IFlow flow)
		{
			this.undoStack.Push (flow);
		}

        public async Task PrepareAsync()
        {
            await this.Peek().PrepareAsync().ConfigureAwait(false);
        }

        public async Task<bool> VerifyAsync()
        {
            return await this.Peek().VerifyAsync().ConfigureAwait(false);
        }

		public async Task<ICase> Forward ()
		{
			
			var cmd = this.Peek ();
			var nextCmd = await cmd.Forward ().ConfigureAwait(false);
			undoStack.Push (nextCmd);
			logger.Debug ("* Forward: {0} -> {1}", cmd.Case.GetType ().FullName, nextCmd.Case.GetType ().FullName);
			return nextCmd.Case;
		}

		public async Task<ICase> Backward ()
		{
			if (undoStack.Count <= 1) { //xx;
				// TODO:log
				return undoStack.Peek ().Case;
			}
			// 現在の情報を捨てる
			var prev = undoStack.Pop ();
			await prev.Backward ();

			var that = this.Peek ();
			while (that.IsAutoForwarding ()) {
				that = undoStack.Pop ();
				await that.Backward ();
			}
			return that.Case;
		}

		public void Refresh ()
		{
			//void is not good.
			undoStack.Clear ();
		}

		public virtual bool OnFinish (IFlow flow)
		{
			//TODO: log. 毎回印刷が終わったら履歴を消す(backできなくする)
			this.Refresh ();
			return true;
		}

		public void SetStartPoint (IFlow flow)
		{
			if (undoStack.Count > 0)
				throw new InvalidOperationException ("already, start flow is set.");
			undoStack.Push (flow);
		}
	}
}


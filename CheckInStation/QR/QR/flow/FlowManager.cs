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

        public IFlow Pop()
        {
            var result = this.undoStack.Pop();
            logger.Trace("Pop(). flow={0}, case={1}", result, result.Case);
            return result;
        }

		public void Push (IFlow flow)
		{
            logger.Trace("Manager.Push(). flow={0}, Case={1}", flow, flow.Case);
			this.undoStack.Push (flow);
		}

        public Task PrepareAsync()
        {
            return this.Peek().PrepareAsync();
        }

        public Task<bool> VerifyAsync()
        {
            return this.Peek().VerifyAsync();
        }

		public async Task<ICase> Forward ()
		{
			
			var cmd = this.Peek ();
			var nextCmd = await cmd.Forward ().ConfigureAwait(false);
			this.Push (nextCmd);
			logger.Debug ("* Forward: {0} -> {1}", cmd.Case.GetType ().FullName, nextCmd.Case.GetType ().FullName);
			return nextCmd.Case;
		}

		public async Task<ICase> Backward ()
		{
			if (undoStack.Count <= 1) { //xx;
                logger.Debug("Backward is empty or one");
				return this.Peek ().Case;
			}
			// 現在の情報を捨てる
			var prev = this.Pop ();
			await prev.Backward ();

			var that = this.Peek ();
            if (that.IsAutoForwarding())
            {
                while (that.IsAutoForwarding())
                {
                    that = this.Pop();
                    await that.Backward();
                }
                this.Push(that);
            }
            logger.Debug("Backward: {0} -> {1}", prev.Case, that.Case);
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


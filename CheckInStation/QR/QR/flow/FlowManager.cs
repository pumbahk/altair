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
				//TODO:LOG
				return new EmptyEvent ();
			}
			return this.RequestBroker.GetInternalEvent ();	
		}

		public async Task<ICase> Forward ()
		{
			
			var cmd = undoStack.Peek ();
			var nextCmd = await cmd.Forward ();
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
			var cmd = undoStack.Pop ();
			return (await cmd.Backward ()).Case;
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


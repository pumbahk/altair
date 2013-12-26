using System;
using System.Collections.Generic;

namespace QR
{
	public class FlowManager
	{
		private Stack<IFlow> undoStack;
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

		public bool Forward (IFlow cmd)
		{
			cmd.Forward ();
			undoStack.Push (cmd);
			return true;
		}

		public bool Backward ()
		{
			if (undoStack.Count <= 0) {
				// TODO:log
				return false;
			}
			var cmd = undoStack.Pop ();
			cmd.Backward ();
			return false;
		}

		public void Refresh ()
		{
			//void is not good.
			undoStack = new Stack<IFlow> ();
		}

		public virtual bool OnFinish (IFlow flow)
		{
			//TODO: log. 毎回印刷が終わったら履歴を消す(backできなくする)
			this.Refresh ();
			return true;
		}
	}
}


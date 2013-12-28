using System;

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

		public virtual bool Verify ()
		{
			var status = Case.Verify ();
			var evStatus = status ? InternalEventStaus.success : InternalEventStaus.failure;
			Manager.GetInternalEvent ().Status = evStatus;
			return status;
		}

		public virtual void Configure ()
		{
			Case.Configure (Manager.GetInternalEvent ());
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

		public ICase NextCase ()
		{
			Configure (); //ここでUIから情報を取得できるようにする必要がある。
			if (Verify ()) {
				return Case.OnSuccess (this);
			} else {
				return Case.OnFailure (this);
			}
		}

		public virtual IFlow Forward ()
		{
			var nextCase = NextCase ();
			if (Case == nextCase) {
				return this;
			}
			return new Flow (Manager, nextCase);
		}

		public IFlow Backward ()
		{
			return this;
		}

		public void Finish ()
		{
			if (!Manager.OnFinish (this)) {
				throw new Exception ("anything is wrong!");
			}
		}
	}
}


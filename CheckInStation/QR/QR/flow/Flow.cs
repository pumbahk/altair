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
			return Case.Verify ();
		}

		public Flow (FlowManager manager, ICase _case)
		{
			Manager = Manager;
			Case = _case;
		}

		public ICase NextCase ()
		{
			Case.Configure ();
			if (Verify ()) {
				return Case.OnSuccess (this);
			} else {
				return Case.OnFailure (this);
			}
		}

		public virtual IFlow Forward ()
		{
			var nextCase = NextCase();
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


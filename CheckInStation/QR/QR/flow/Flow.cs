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

		public FlowState State { get; set; }

		public FlowManager Manager { get; set; }

		public IFlow Forward ()
		{
			ICase nextCase;

			Case.Configure ();
			if (Case.Verify ()) {
				nextCase = Case.OnSuccess (this);
			} else {
				nextCase = Case.OnFailure (this);
			}
			return new Flow (){ Case = nextCase };
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


using System;

namespace QR
{
	public abstract class AbstractCase :ICase
	{
		public virtual IResource Resource{ get; set; }

		public AbstractCase (IResource resource)
		{
			Resource = resource;
		}

		public virtual void Configure ()
		{
		}

		public virtual bool Verify ()
		{
			return true;
		}

		public virtual ICase OnFailure (IFlow flow)
		{
			//TODO:log message
			throw new InvalidOperationException ("must be success");
		}

		public abstract ICase OnSuccess (IFlow flow);



		public virtual bool OnRefresh (FlowManager m)
		{
			return true; //do something
		}
	}
}


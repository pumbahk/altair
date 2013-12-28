using System;

namespace QR
{
	public abstract class AbstractCase
	{
		public virtual IResource Resource{ get; set; }
		public IInternalEvent PresentationChanel { get; set; }
		public AbstractCase (IResource resource)
		{
			Resource = resource;
		}

		public virtual void Configure (IInternalEvent ev)
		{
			this.PresentationChanel = ev;
		}

		public virtual void Configure()
		{
			Configure (new EmptyEvent ());
		}

		public virtual bool Verify ()
		{
			return true;
		}
		public virtual ICase OnFailure (IFlow flow)
		{
			throw new InvalidOperationException ("must be success");
		}

		public abstract ICase OnSuccess (IFlow flow);



		public virtual bool OnRefresh (FlowManager m)
		{
			return true; //do something
		}
	}
}


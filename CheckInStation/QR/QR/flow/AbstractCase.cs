using System;
using System.Threading.Tasks;

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


		public virtual Task PrepareAsync (IInternalEvent ev)
		{
			return Task.Run (() => {
				this.PresentationChanel = ev;
			});
		}

		public virtual Task PrepareAsync ()
		{
			return PrepareAsync (new EmptyEvent ());
		}


		public virtual async Task<bool> VerifyAsync ()
		{
			return await Task.Run (() => {
				return true;
			}).ConfigureAwait (false);
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


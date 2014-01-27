using System;
using System.Threading.Tasks;
using NLog;
using QR.message;

namespace QR
{
	public abstract class AbstractCase : ICase
	{
        private Logger logger = LogManager.GetCurrentClassLogger();
		public virtual IResource Resource{ get; set; }

		public IInternalEvent PresentationChanel { get; set; }

        public virtual string Description
        {
            get {
                try{
                  return this.Resource.GetCaseDescriptionMessage(this as ICase);
                }
                catch (Exception ex)
                  {
                    logger.ErrorException("missing:", ex);
                    return "<à–¾‚ªÝ’è‚³‚ê‚Ä‚Ü‚¹‚ñ!!>";
                  }
            }
        }

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
			flow.Finish ();
			return new CaseFailureRedirect (Resource);
		}

		public abstract ICase OnSuccess (IFlow flow);

		public virtual bool OnRefresh (FlowManager m)
		{
			return true; //do something
		}
	}
}


using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.message;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    public abstract class AbstractCase : ICase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public virtual IResource Resource{ get; set; }

        private IInternalEvent _presentationChanel;
        public IInternalEvent PresentationChanel { 
            get {
                if (this._presentationChanel == null) {
                    logger.Warn ("use presentation chanel before binding event.".WithMachineName());
                    this._presentationChanel = new EmptyEvent ();
                }
                return this._presentationChanel;
            }
            set{ this._presentationChanel = value; }
        }

        public virtual string Description
        {
            get {
                try{
                  return this.Resource.GetCaseDescriptionMessage(this as ICase);
                }
                catch (Exception ex)
                  {
                    logger.ErrorException("missing:".WithMachineName(), ex);
                    return "<??????????????????????!!>";
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

        public virtual Task<bool> VerifyAsync ()
        {
            return Task.Run(() =>
            {
                return true;
            });
        }

        public virtual ICase OnFailure(IFlow flow)
        {
            flow.Finish();
            var message = this.PresentationChanel.GetMessageString();
            if (message == "")
                return new CaseFailureRedirect(Resource);
            else
                return new CaseFailureRedirect(Resource, message);
        }

        public abstract ICase OnSuccess (IFlow flow);

        public virtual bool OnRefresh (FlowManager m)
        {
            return true; //do something
        }
    }
}


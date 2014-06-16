using NLog;
using System;
using System.Threading.Tasks;
using checkin.core.support;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.core
{
    /// <summary>
    /// Application. [Presentation Layer] --RequestBroker--  [Domain Layer]
    /// </summary>
    public class RequestBroker
    {
        public FlowManager FlowManager { get; set; }

        public IInternalEvent Event { get; set; }

        private Logger logger = LogManager.GetCurrentClassLogger();

        public RequestBroker (FlowManager manager)
        {
            this.FlowManager = manager;
            FlowManager.RequestBroker = this;
        }
        
        public bool IsConfigurationOK ()
        {
            if (FlowManager == null) {
                throw new InvalidOperationException ("flow manager is null");
            }
            if (FlowManager.RequestBroker != this) {
                throw new InvalidOperationException ("anything is wrong(FlowManager.RequestBroker != <me>)");
            }
            return true;
        }

        public IInternalEvent GetInternalEvent ()
        {
            if (Event == null) {
                logger.Warn("Internal Event is not found.".WithMachineName());
                return new EmptyEvent (); //TODO:implement
            } else {
                return Event;
            }
        }

        public Task PrepareAsync(IInternalEvent ev)
        {
            this.Event = ev;//xxx:
            return this.FlowManager.PrepareAsync();
        }

        public Task<bool> VerifyAsync(IInternalEvent ev)
        {
            this.Event = ev;//xxx:
            return this.FlowManager.VerifyAsync();
        }

        public Task<ICase> SubmitAsync (IInternalEvent ev)
        {
            this.Event = ev;//xxx:
            return this.FlowManager.Forward();
        }

        public Task<ICase> BackwardAsync()
        {
            return this.FlowManager.Backward();
        }

        public ICase RedirectAlternativeCase(ICase previous)
        {
            return this.FlowManager.RedirectAlternativeFlow(previous).Case;
        }

        public void SetStartCase (ICase case_)
        {
            this.FlowManager.SetStartPoint (new Flow (this.FlowManager, case_));
        }
    }
}

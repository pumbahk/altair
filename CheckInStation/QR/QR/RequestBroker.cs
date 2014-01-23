using NLog;
using System;
using System.Threading.Tasks;

namespace QR
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
                logger.Warn("Internal Event is not found.");
				return new EmptyEvent (); //TODO:implement
			} else {
				return Event;
			}
		}

        public async Task PrepareAsync(IInternalEvent ev)
        {
            logger.Debug("ev: {0}", ev);
            this.Event = ev;//xxx:
            await this.FlowManager.PrepareAsync().ConfigureAwait(false);
        }

        public async Task<bool> VerifyAsync(IInternalEvent ev)
        {
            logger.Debug("ev: {0}", ev);
            this.Event = ev;//xxx:
            return await this.FlowManager.VerifyAsync().ConfigureAwait(false);
        }

		public async Task<ICase> SubmitAsync (IInternalEvent ev)
		{
            logger.Debug("ev: {0}", ev);
			this.Event = ev;//xxx:
			var result = await this.FlowManager.Forward().ConfigureAwait(false);
            return result;
		}

        public async Task<ICase> BackwardAsync()
        {
            return await this.FlowManager.Backward().ConfigureAwait(false);
        }

		public void SetStartCase (ICase case_)
		{
			this.FlowManager.SetStartPoint (new Flow (this.FlowManager, case_));
		}
	}
}

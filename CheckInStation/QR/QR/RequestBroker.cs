using System;

namespace QR
{
	/// <summary>
	/// Application. [Presentation Layer] --RequestBroker--  [Domain Layer]
	/// </summary>
	public class RequestBroker
	{
		public FlowManager FlowManager { get; set; }

		public IInternalEvent Event { get; set; }

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
				//TODO:login
				return new EmptyEvent (); //TODO:implement
			} else {
				return Event;
			}
		}
	}
}


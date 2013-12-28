using System;

namespace QR
{
	public class Application
	{
		public RequestBroker RequestBroker { get; set; }

		public FlowManager FlowManager { get; set; }

		public IResource Resource { get; set; }

		public Application ()
		{
			var config = new Configurator (new Resource (true));
			this.Resource = config.Resource;
			config.Include (AuthConfiguration.IncludeMe);
			config.Include (QRConfiguration.IncludeMe);
			config.Include (HttpCommunicationConfiguration.IncludeMe);

			this.FlowManager = new FlowManager (new FlowDefinitionDefault ());
			this.RequestBroker = new RequestBroker (FlowManager);

			// verify
			if (!this.RequestBroker.IsConfigurationOK () || !config.Verify ()) {
				throw new InvalidProgramException ("configuration is not end");
			}
		}

		public async void Run (ICase case_)
		{
			this.RequestBroker.SetStartCase (case_);
			var p = new QR.presentation.cli.AuthInput (RequestBroker); //todo:change
			p.Run ();
		}
	}
}


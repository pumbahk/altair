using System;
using System.Threading.Tasks;

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

		public async Task Run (ICase case_)
		{
			this.RequestBroker.SetStartCase (case_);
			var p = new QR.presentation.cli.AuthInput (RequestBroker, case_); //todo:change
			ICase qrCase = await p.Run ();
			var q = new QR.presentation.cli.QRInput (RequestBroker, qrCase);
			ICase svgCase = await q.Run ();
		}
	}
}


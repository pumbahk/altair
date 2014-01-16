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
			config.Include (AuthConfiguration.MockIncludeMe);
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
			ICase authedCase = await p.Run ();
			var q = new QR.presentation.cli.SelectInputStrategy (RequestBroker, authedCase);
			ICase selectedCase = await q.Run ();

			if (selectedCase is CaseQRCodeInput) {
				var r = new QR.presentation.cli.QRInput (RequestBroker, selectedCase);
				while (true) {
					await r.Run ();
				}
			} else if (selectedCase is CaseOrdernoOrdernoInput) {
				var r = new QR.presentation.cli.OrdernoInput (RequestBroker, selectedCase);
				while (true) {
					await r.Run ();
				}
			}
		}
	}
}
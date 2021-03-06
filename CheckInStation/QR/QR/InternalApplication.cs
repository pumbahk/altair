using NLog;
using System;
using System.Threading.Tasks;
using QR.support;

namespace QR    
{
    public class InternalApplication
    {
        public RequestBroker RequestBroker { get; set; }

        public FlowManager FlowManager { get; set; }

        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger();

        public InternalApplication ()
        {
            if (!logger.IsInfoEnabled)
            {
                throw new InvalidOperationException("logger is disabled");
            }
            logger.Info("Internal Application starting.".WithMachineName());
            var config = new Configurator (new Resource (true));
            this.Resource = config.Resource;
            //config.Include (AuthConfiguration.MockIncludeMe);
            config.Include(AuthConfiguration.IncludeMe);
            config.Include (QRConfiguration.IncludeMe);
            config.Include (HttpCommunicationConfiguration.IncludeMe);

            this.FlowManager = new FlowManager (new EaglesFlowDefinition ());
            this.RequestBroker = new RequestBroker (FlowManager);

            // verify
            logger.Info("internal Application configuration checking.".WithMachineName());
            if (!this.RequestBroker.IsConfigurationOK () || !config.Verify ()) {
                throw new InvalidProgramException ("configuration is not end");
            }
        }
        public void ShutDown()
        {
            logger.Info("Internal Application shutdown.".WithMachineName());
        }

        public async Task Run (ICase case_)
        {
            this.RequestBroker.SetStartCase (case_);
            var p = new QR.presentation.cli.AuthInput (RequestBroker, case_); //todo:change

            ICase authedCase = await p.Run ();

            // 別のスレッドで取りたい。本当は
            await this.Resource.AdImageCollector.Run (this.Resource.EndPoint.AdImages).ConfigureAwait(false);

            var q = new QR.presentation.cli.SelectInputStrategy (RequestBroker, authedCase);
            ICase selectedCase = await q.Run ().ConfigureAwait(false);

            if (selectedCase is CaseQRCodeInput) {
                var r = new QR.presentation.cli.QRInput (RequestBroker, selectedCase);
                while (true) {
                    await r.Run ().ConfigureAwait(false);
                }
            } else if (selectedCase is CaseOrdernoOrdernoInput) {
                var r = new QR.presentation.cli.OrdernoInput (RequestBroker, selectedCase);
                while (true) {
                    await r.Run ().ConfigureAwait(false);
                }
            }
        }
    }
}
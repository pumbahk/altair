using NLog;
using System;
using System.Threading.Tasks;
using checkin.core.support;
using checkin.core;
using checkin.core.flow;
using checkin.core.events;
using checkin.core.models;
using checkin.config;

namespace checkin.presentation
{
    public class InternalApplication
    {
        public RequestBroker RequestBroker { get; set; }

        public FlowManager FlowManager { get; set; }

        public IResource Resource { get; set; }

        private static Logger logger = LogManager.GetCurrentClassLogger();

        public IFlowDefinition CreateFlowDefinition(IConfigurator config)
        {
            switch (config.FlowDefinitionType)
            {
                case FlowDefinitionType.QRFront:
                    return new EaglesFlowDefinition();
                case FlowDefinitionType.OrdernoFront:
                    return new VisselFlowDefinition();
                case FlowDefinitionType.CommonMode:
                    return new CommonFlowDefinition();
                case FlowDefinitionType.StandardFlow:
                    return new StandardFlowDefinition();
                default:
                    throw new InvalidOperationException("anything is wrong");
            }         
        }

        public InternalApplication ()
        {
            if (!logger.IsInfoEnabled)
            {
                throw new InvalidOperationException("logger is disabled");
            }
            logger.Info("Internal Application starting.".WithMachineName());
            var config = new Configurator (new Resource (true));
            this.Resource = config.Resource;
            config.Include(AuthConfiguration.IncludeMe);
            config.Include (QRConfiguration.IncludeMe);
            config.Include (HttpCommunicationConfiguration.IncludeMe);
            this.Resource.FlowDefinition = this.CreateFlowDefinition(config);
            this.FlowManager = new FlowManager(this.Resource.FlowDefinition);
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
            var p = new checkin.presentation.cli.AuthInput (RequestBroker, case_); //todo:change

            ICase authedCase = await p.Run ();

            // 別のスレッドで取りたい。本当は
            await this.Resource.AdImageCollector.Run (this.Resource.EndPoint.AdImages).ConfigureAwait(false);

            var q = new checkin.presentation.cli.SelectInputStrategy (RequestBroker, authedCase);
            ICase selectedCase = await q.Run ().ConfigureAwait(false);

            if (selectedCase is CaseQRCodeInput) {
                var r = new checkin.presentation.cli.QRInput (RequestBroker, selectedCase);
                while (true) {
                    await r.Run ().ConfigureAwait(false);
                }
            } else if (selectedCase is CaseOrdernoOrdernoInput) {
                var r = new checkin.presentation.cli.OrdernoInput (RequestBroker, selectedCase);
                while (true) {
                    await r.Run ().ConfigureAwait(false);
                }
            }
        }
    }
}
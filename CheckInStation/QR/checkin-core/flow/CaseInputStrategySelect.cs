using System;
using System.Threading.Tasks;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core.message;

namespace checkin.core.flow
{
    /// <summary>
    /// Case qr input select. 認証方法選択画面
    /// </summary>
    public class CaseInputStrategySelect :AbstractCase, ICase
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public InputUnit Unit { get; set; }

        public CaseInputStrategySelect (IResource resource) : base (resource)
        {
        }

        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                var subject = PresentationChanel as SelectInputStragetyEvent;
                InputUnit unit;
                bool status;
                if (subject.InputUnitString == null) {
                    logger.Warn("subject.InputUnitString is null".WithMachineName());
                    unit = InputUnit.qrcode;
                    status = true;
                } else {
                    status = EnumUtil.TryParseEnum<InputUnit>(subject.InputUnitString, out unit);
                }
                subject.InputUnit = Unit = unit;
                return status;
            });
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return flow.GetFlowDefinition ().AfterSelectInputStrategy (this.Resource, this.Unit);
        }

        public override ICase OnFailure (IFlow flow)
        {
            return this;
        }
    }
}

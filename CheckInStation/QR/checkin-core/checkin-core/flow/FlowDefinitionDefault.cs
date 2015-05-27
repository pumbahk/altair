using System;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;

namespace checkin.core.flow
{
    public class DefaultFlowDefinition: IFlowDefinition
    {
        public InputUnit CurrentInputUnit { get; set; }

        public DefaultFlowDefinition()
        {
            this.CurrentInputUnit = InputUnit.before_auth;
        }

        
        public ICase AfterFailureRedirect (IResource resource)
        {
            return DispatchICaseUtil.GetInputCaseByInputUnit (resource, this.CurrentInputUnit);
        }

        public ICase AfterAuthorization (IResource resource)
        {
            return new CaseInputStrategySelect (resource);
        }

        public ICase AfterWelcome(IResource resource, int printtype)
        {
            this.CurrentInputUnit = InputUnit.qrcode;
            return new CaseQRCodeInput(resource);
        }

        public ICase AfterCountChoice(IResource resource, int printtype, TicketData tdata)
        {
            this.CurrentInputUnit = InputUnit.qrcode;
            return new CaseQRCodeInput(resource);
        }

        public ICase AfterTicketChoice(IResource resource, int printcount, TicketData tdata)
        {
            this.CurrentInputUnit = InputUnit.qrcode;
            return new CaseQRCodeInput(resource);
        }

        public ICase AfterOrdernoConfirmed(IResource resource, VerifiedOrdernoRequestData verifieddata)
        {
            return new CaseOrdernoConfirmForAll(resource, verifieddata);
        }

        public ICase AfterSelectInputStrategy (IResource resource, InputUnit Selected)
        {
            this.CurrentInputUnit = Selected;
            return DispatchICaseUtil.GetInputCaseByInputUnit (resource, this.CurrentInputUnit);
        }

        public ICase AfterQRDataFetch(IResource resource, TicketData tdata)
        {
            return new CaseQRConfirmForOne(resource, tdata);
        }
        public ICase AfterPrintFinish (IResource resource)
        {
            return DispatchICaseUtil.GetInputCaseByInputUnit (resource, this.CurrentInputUnit);
        }

        public ICase PreviousCaseFromRedirected(IResource resource)
        {
            return new CaseInputStrategySelect(resource);
        }

        public ICase GetAlternativeCase (ICase previous)
        {
            throw new InvalidOperationException("not supported");
        }

    }


    class DispatchICaseUtil
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public static ICase GetInputCaseByInputUnit (IResource resource, InputUnit Selected)
        {
            logger.Debug("InputUnit: {0}.. lookup redirect point.".WithMachineName(), Selected.ToString ());
            switch (Selected) {
            case InputUnit.qrcode:
                return new CaseQRCodeInput (resource);
            case InputUnit.order_no:
                return new CaseOrdernoOrdernoInput (resource);
            case InputUnit.before_auth:
                return new CaseAuthInput (resource);
            default:
                logger.Info("InputUnit: {0} is unknown value. default={1} is selected".WithMachineName(), Selected.ToString (), default(InputUnit));
                return new CaseQRCodeInput (resource);
            }
        }
    }
}


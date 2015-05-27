using System;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core.flow;

namespace checkin.core.flow
{

    public class QRAllOnceFlowDefinition : IFlowDefinition
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

        public InputUnit CurrentInputUnit { get; set; }

        public QRAllOnceFlowDefinition()
        {
            this.CurrentInputUnit = InputUnit.before_auth;
        }

        public ICase AfterFailureRedirect(IResource resource)
        {
            return DispatchICaseUtil.GetInputCaseByInputUnit(resource, this.CurrentInputUnit);
        }

        public ICase AfterAuthorization(IResource resource)
        {
            //this.CurrentInputUnit = InputUnit.qrcode;
            //return new CaseQRCodeInput(resource);
            return new CaseWelcome(resource);
        }

        public ICase AfterWelcome(IResource resource)
        {
            this.CurrentInputUnit = InputUnit.qrcode;
            return new CaseQRCodeInput(resource);
        }

        public ICase AfterSelectInputStrategy(IResource resource, InputUnit Selected)
        {
            throw new InvalidOperationException("dont call this");
        }

        public ICase AfterQRDataFetch(IResource resource, TicketData tdata)
        {
            return new CaseQRConfirmForAll(resource, tdata);
            //return new CaseQRConfirmForAllHidden(resource, tdata);
        }

        public ICase AfterPrintFinish(IResource resource)
        {
            return this.AfterAuthorization(resource);
        }

        public ICase PreviousCaseFromRedirected(IResource resource)
        {
            return this.AfterAuthorization(resource);
        }

        public ICase GetAlternativeCase(ICase previous)
        {
            switch (this.CurrentInputUnit)
            {
                case InputUnit.qrcode:
                    this.CurrentInputUnit = InputUnit.order_no;
                    return new CaseOrdernoOrdernoInput(previous.Resource);
                case InputUnit.order_no:
                    this.CurrentInputUnit = InputUnit.qrcode;
                    return
                        new CaseQRCodeInput(previous.Resource);
                default:
                    logger.Warn("invalid redirect is found. (get alternative case from {0})".WithMachineName(), previous);
                    this.CurrentInputUnit = InputUnit.before_auth;
                    return new CaseAuthInput(previous.Resource);
            }
        }
    }
}

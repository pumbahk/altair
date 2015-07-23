using System;
using NLog;
using checkin.core.support;
using checkin.core.events;
using checkin.core.models;
using checkin.core.flow;

namespace checkin.core.flow
{

    public class OneStepFlowDefinition : IFlowDefinition
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

        public InputUnit CurrentInputUnit { get; set; }

        public OneStepFlowDefinition()
        {
            this.CurrentInputUnit = InputUnit.before_auth;
        }

        public ICase AfterFailureRedirect(IResource resource)
        {
            return DispatchICaseUtil.GetInputCaseByInputUnit(resource, this.CurrentInputUnit);
        }

        public ICase AfterAuthorization(IResource resource)
        {
            this.CurrentInputUnit = InputUnit.qrcode;
            return new CaseQRCodeInput(resource);
        }

        public ICase AfterWelcome(IResource resource, int printtype)
        {
            if (printtype == 0)
            {
                this.CurrentInputUnit = InputUnit.qrcode;
                return new CaseQRCodeInput(resource);
            }
            else
            {
                this.CurrentInputUnit = InputUnit.order_no;
                return new CaseOrdernoOrdernoInput(resource);
            }

        }

        public ICase AfterCountChoice(IResource resource, int printcount, TicketData tdata)
        {
            //一枚発券
            if (printcount == 0)
            {

                //return new CaseQRConfirmForOne(resource, tdata);
                return new CaseConfirmListForOne(resource, tdata);
            }
            //複数発券
            else
            {
                return new CasePartOrAll(resource, tdata);
            }

        }

        public ICase AfterTicketChoice(IResource resource, int printcount, TicketData tdata)
        {
            //複数発券
            if (printcount == 0)
            {

                return new CaseQRConfirmForAll(resource, tdata, 0);
            }
            //全部発券
            else
            {
                return new CaseQRConfirmForAll(resource, tdata, 1);
                //return new CaseConfirmListForAll(resource, tdata);
            }
        }

        public ICase AfterTicketChoice(IResource resource, int printcount, VerifiedOrdernoRequestData verifieddata)
        {
            //複数発券
            if (printcount == 0)
            {

                return new CaseOrdernoConfirmForAll(resource, verifieddata, 0);
            }
            //全部発券
            else
            {
                return new CaseOrdernoConfirmForAll(resource, verifieddata, 1);
            }
        }

        public ICase AfterOrdernoConfirmed(IResource resource, VerifiedOrdernoRequestData verifieddata)
        {
            return new CaseOrdernoConfirmForAllHidden(resource, verifieddata);
        }

        public ICase AfterSelectInputStrategy(IResource resource, InputUnit Selected)
        {
            throw new InvalidOperationException("dont call this");
        }

        public ICase AfterQRDataFetch(IResource resource, TicketData tdata)
        {
            //return new CaseQRConfirmForAll(resource, tdata);
            return new CaseQRConfirmForAllHidden(resource, tdata);
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
                    return new CaseQRCodeInput(previous.Resource);
                case InputUnit.order_no:
                    this.CurrentInputUnit = InputUnit.qrcode;
                    return
                        new CaseOrdernoOrdernoInput(previous.Resource);
                default:
                    logger.Warn("invalid redirect is found. (get alternative case from {0})".WithMachineName(), previous);
                    this.CurrentInputUnit = InputUnit.before_auth;
                    return new CaseAuthInput(previous.Resource);
            }
        }
    }
}

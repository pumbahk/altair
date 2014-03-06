using System;
using NLog;

namespace QR
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

	public class EaglesFlowDefinition : IFlowDefinition
	{
        private static Logger logger = LogManager.GetCurrentClassLogger();

		public InputUnit CurrentInputUnit { get; set; }

		public EaglesFlowDefinition ()
		{
			this.CurrentInputUnit = InputUnit.before_auth;
		}
		
		public ICase AfterFailureRedirect (IResource resource)
		{
			return DispatchICaseUtil.GetInputCaseByInputUnit (resource, this.CurrentInputUnit);
		}
		
		public ICase AfterAuthorization (IResource resource)
		{
            this.CurrentInputUnit = InputUnit.qrcode;
			return new CaseQRCodeInput(resource);
		}
		
		public ICase AfterSelectInputStrategy (IResource resource, InputUnit Selected)
		{
			throw new InvalidOperationException("dont call this");
		}

		public ICase AfterQRDataFetch(IResource resource, TicketData tdata)
		{
			return new CaseQRConfirmForAll(resource, tdata);
		}

		public ICase AfterPrintFinish (IResource resource)
		{
			return this.AfterAuthorization(resource);
		}

		public ICase PreviousCaseFromRedirected(IResource resource)
		{
			return this.AfterAuthorization (resource);
		}

        public ICase GetAlternativeCase (ICase previous)
        {
            switch(this.CurrentInputUnit)
            {
                case InputUnit.qrcode:
                    this.CurrentInputUnit = InputUnit.order_no;
                    return new CaseOrdernoOrdernoInput(previous.Resource);
                case InputUnit.order_no:
                    this.CurrentInputUnit = InputUnit.qrcode;
                    return new CaseQRCodeInput(previous.Resource);
                default:
                    logger.Warn("invalid redirect is found. (get alternative case from {0})", previous);
                    this.CurrentInputUnit = InputUnit.before_auth;
                    return new CaseAuthInput(previous.Resource);
            }
        }
	}

	class DispatchICaseUtil
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public static ICase GetInputCaseByInputUnit (IResource resource, InputUnit Selected)
		{
			logger.Debug ("InputUnit: {0}.. lookup redirect point.", Selected.ToString ());
			switch (Selected) {
			case InputUnit.qrcode:
				return new CaseQRCodeInput (resource);
			case InputUnit.order_no:
				return new CaseOrdernoOrdernoInput (resource);
			case InputUnit.before_auth:
				return new CaseAuthInput (resource);
			default:
				logger.Info ("InputUnit: {0} is unknown value. default={1} is selected", Selected.ToString (), default(InputUnit));
				return new CaseQRCodeInput (resource);
			}
		}
	}
}


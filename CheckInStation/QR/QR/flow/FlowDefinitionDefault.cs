using System;
using NLog;

namespace QR
{
	public class FlowDefinitionDefault : IFlowDefinition
	{
		public InputUnit CurrentInputUnit { get; set; }

		public FlowDefinitionDefault ()
		{
			this.CurrentInputUnit = InputUnit.before_auth;
		}

		public ICase AfterFailureRedirect (ICase case_)
		{
			return AfterFailureRedirect (case_.Resource);
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

		public ICase AfterPrintFinish (IResource resource)
		{
			return DispatchICaseUtil.GetInputCaseByInputUnit (resource, this.CurrentInputUnit);
		}

		public ICase PreviousCaseFromRedirected(IResource resource)
		{
			return new CaseInputStrategySelect(resource);
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


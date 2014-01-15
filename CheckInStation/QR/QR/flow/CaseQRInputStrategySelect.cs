using System;
using System.Threading.Tasks;
using NLog;

namespace QR
{
	/// <summary>
	/// Case qr input select. 認証方法選択画面
	/// </summary>
	public class CaseQRInputStrategySelect :AbstractCase, ICase
	{
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public InputUnit Unit { get; set; }

		public CaseQRInputStrategySelect (IResource resource) : base (resource)
		{
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				var subject = PresentationChanel as QRInputEvent;
				InputUnit unit;
				var status = subject.TryParseEnum<InputUnit> (subject.InputUnitString, out unit);
				subject.InputUnit = Unit = unit;
				return status;
			});
		}

		public override ICase OnSuccess (IFlow flow)
		{
			switch (Unit) {
			case InputUnit.qrcode:
				return new CaseQRCodeInput (Resource);
			case InputUnit.order_no:
				throw new NotImplementedException ();
			default:
				logger.Info ("InputUnit: {0} is unknown value. default={1} is selected", Unit.ToString(), default(InputUnit));
				return new CaseQRCodeInput (Resource);
			}
		}

		public override ICase OnFailure (IFlow flow)
		{
			return this;
		}
	}
}

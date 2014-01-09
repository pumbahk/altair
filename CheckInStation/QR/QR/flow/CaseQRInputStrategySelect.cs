using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case qr input select. 認証方法選択画面
	/// </summary>
	public class CaseQRInputStrategySelect :AbstractCase, ICase
	{
		public InputUnit InputUnit { get; set; }

		public CaseQRInputStrategySelect (IResource resource) : base (resource)
		{
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				try {
					var subject = PresentationChanel as QRInputEvent;
					InputUnit = (InputUnit)Enum.Parse (typeof(InputUnit), subject.InputUnitString);
					subject.InputUnit = InputUnit;
					return true;
				} catch (Exception e) {
					Console.WriteLine (e.ToString ());
					return false;
				}
			});
		}

		public override ICase OnSuccess (IFlow flow)
		{
			switch (InputUnit) {
			case InputUnit.qrcode:
				return new CaseQRCodeInput (Resource);
			case InputUnit.orderno:
				throw new NotImplementedException ();
			default:
				throw new NotImplementedException ();
			}
		}

		public override ICase OnFailure (IFlow flow)
		{
			return this;
		}
	}
}

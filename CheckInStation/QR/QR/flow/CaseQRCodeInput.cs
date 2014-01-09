using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	/// <summary>
	/// Case QR code input. QR読み込み
	/// </summary>
	/// 
	public class CaseQRCodeInput :AbstractCase, ICase
	{
		public string QRCode { get; set; }

		public override Task ConfigureAsync (IInternalEvent ev)
		{
			QRInputEvent subject = ev as QRInputEvent;
			this.QRCode = subject.QRCode;
			return base.ConfigureAsync (ev);
		}

		public override Task<bool> VerifyAsync ()
		{
			return Task.Run (() => {
				return true;
			}); //tODO:２度調べるを防止
		}

		public CaseQRCodeInput (IResource resource) : base (resource)
		{
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRDataFetch (Resource, QRCode);
		}

		public override ICase OnFailure (IFlow flow)
		{
			return new CaseFailureRedirect (Resource);
		}
	}

	public enum PrintUnit
	{
		one,
		all
	}
}


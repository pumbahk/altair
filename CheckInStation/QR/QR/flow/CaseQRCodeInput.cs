using System;
using System.Threading.Tasks;

namespace QR
{
	/// <summary>
	/// Case QR code input. QR読み込み
	/// </summary>
	public class CaseQRCodeInput :AbstractCase, ICase
	{
		public IVerifier<string>QRCodeVerifier { get; set; }

		public string QRCode { get; set; }

		public int VerifiedCount{ get; set; }
		//hmm.
		private bool VerifyStatus;

		public CaseQRCodeInput (IResource resource) : base (resource)
		{
			this.VerifiedCount = 0; //2度調べるを防止したい
			this.VerifyStatus = false;
		}

		public override Task ConfigureAsync (IInternalEvent ev)
		{
			return Task.Run (() => {
				QRInputEvent subject = ev as QRInputEvent;
				this.QRCodeVerifier = this.Resource.QRCodeVerifier;
				this.QRCode = subject.QRCode;
			});
		}

		public override async Task<bool> VerifyAsync ()
		{
			if (this.VerifiedCount > 0) {
				return this.VerifyStatus;
			}
			this.VerifyStatus = await this.QRCodeVerifier.VerifyAsync (this.QRCode);
			this.VerifiedCount += 1;
			return this.VerifyStatus;
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


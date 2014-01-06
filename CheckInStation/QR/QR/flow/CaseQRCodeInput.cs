using System;

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

		public override void Configure (IInternalEvent ev)
		{
			QRInputEvent subject = ev as QRInputEvent;
			this.QRCodeVerifier = this.Resource.QRCodeVerifier;
			this.QRCode = subject.QRCode;
		}

		public override bool Verify ()
		{
			if (this.VerifiedCount > 0) {
				return this.VerifyStatus;
			}
			var t = this.QRCodeVerifier.VerifyAsync (this.QRCode);
			t.Wait ();
			this.VerifyStatus = t.Result;
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


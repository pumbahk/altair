using System;

namespace QR
{
	public class QRCodeVerifier : IVerifier<string>
	{
		public QRCodeVerifier ()
		{
		}

		public bool Verify(string qrcode)
		{
			return true; //TODO:implement
		}
	}
}


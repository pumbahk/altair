using System;

namespace QR
{
	public class FakeResource :IResource
	{
		public IDataLoader<string> QRCodeLoader { get; set; }

		public IVerifier<string> QRCodeVerifier { get; set; }

		public AuthInfo AuthInfo { get; set; }

		public IAuthentication Authentication { get; set; }
	}
}


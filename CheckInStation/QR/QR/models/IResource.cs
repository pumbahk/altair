using System;

namespace QR
{
	public interface IResource
	{
		IVerifier<string> QRCodeVerifier { get; set;}
		IDataLoader<string> QRCodeLoader {get; set;}
	}
}


using System;

namespace QR
{
	public interface IAuthentication
	{
		AuthInfo auth(IResource resource, string name, string password);
	}
}


using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	public interface IAuthentication
	{
		Task<ResultTuple<string, AuthInfo>> AuthAsync(IResource resource, string name, string password);
	}
}


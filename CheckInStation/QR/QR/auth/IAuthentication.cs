using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IAuthentication
	{
		Task<ResultTuple<string, AuthInfo>> AuthAsync(IResource resource, string name, string password);
	}
}


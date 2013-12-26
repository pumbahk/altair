using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IAuthentication
	{
		Task<ResultTuple<string, AuthInfo>> authAsync(IResource resource, string name, string password);
	}
}


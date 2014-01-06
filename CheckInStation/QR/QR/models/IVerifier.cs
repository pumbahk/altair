using System;
using System.Threading.Tasks;

namespace QR
{
	public interface IVerifier<T>
	{
		bool Verify(T target);
		Task<bool> VerifyAsync(T target);
	}
}


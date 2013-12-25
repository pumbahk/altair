using System;

namespace QR
{
	public interface IVerifier<T>
	{
		bool Verify(T target);
	}
}


using System;

namespace QR
{
	public class FakeVerifier<T> : IVerifier<T>
	{
		public bool Result { get; set;}
		public FakeVerifier (bool result)
		{
			Result = result;
		}
		public bool Verify(T target){
			return Result;
		}
	}
}


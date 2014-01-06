using System;
using System.Threading.Tasks;

namespace QR
{
	public class FakeVerifier<T> : IVerifier<T>
	{
		public bool Result { get; set; }

		public FakeVerifier (bool result)
		{
			Result = result;
		}

		public bool Verify (T target)
		{
			return Result;
		}

		public Task<bool> VerifyAsync (T target)
		{
			var taskSource = new TaskCompletionSource<bool> ();
			taskSource.SetResult (Result);
			return taskSource.Task;
		}
	}
}


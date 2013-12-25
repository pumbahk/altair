using System;

namespace QR
{
	public class FakeDataLoader<T> :IDataLoader<T>
	{
		public T Result{ get; set;}
		public FakeDataLoader (T result)
		{
			Result = result;
		}
	}
}


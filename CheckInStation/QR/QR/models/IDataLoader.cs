using System;

namespace QR
{
	public interface IDataLoader<T>
	{
		T Result {get; set;}
	}
}


using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
	public interface IDataFetcher<G,T>
	{
		Task<ResultTuple<string, T>> FetchAsync(G arg);
	}
}


using System;
using QR.message;
using System.Threading.Tasks;

namespace QR
{
    public class FakeDataLoader<G,T> :IDataFetcher<G,T>
    {
        public T Result{ get; set; }

        public FakeDataLoader (T result)
        {
            Result = result;
        }

        public Task<ResultTuple<string, T>> FetchAsync (G arg)
        {
            return Task.Run (() => {
                return new Success<string,T> (Result) as ResultTuple<string,T>;
            });
        }
    }
}


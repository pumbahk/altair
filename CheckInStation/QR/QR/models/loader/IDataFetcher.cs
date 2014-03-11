using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
    public interface IDataFetcher<Required,Provided>
    {
        Task<ResultTuple<string, Provided>> FetchAsync(Required arg);
    }
}


using System;
using System.Threading.Tasks;
using checkin.core.message;

namespace checkin.core.models
{
    public interface IDataFetcher<Required,Provided>
    {
        Task<ResultTuple<string, Provided>> FetchAsync(Required arg);
    }
}


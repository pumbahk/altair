using System;
using System.Threading.Tasks;
using checkin.core.message;
using checkin.core.models;

namespace checkin.core.auth
{
    public interface IAuthentication
    {
        IResource Resource{ get; set; }

        Task<ResultTuple<string, AuthInfo>> AuthAsync (string name, string password);

        string LoginURL { get; set; }
        
    }
}


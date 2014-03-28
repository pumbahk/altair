using System;
using System.Threading.Tasks;
using QR.message;

namespace QR
{
    public interface IAuthentication
    {
        IResource Resource{ get; set; }

        Task<ResultTuple<string, AuthInfo>> AuthAsync (string name, string password);

        string LoginURL { get; set; }
        
    }
}


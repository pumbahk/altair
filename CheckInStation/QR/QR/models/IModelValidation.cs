using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using QR.message;

namespace QR
{
    using Result = ResultTuple<string, bool>;

    public interface IModelValidation
    {
        Result ValidateAuthLoginName(string name);
        Result ValidateAuthPassword(string password);
        Result ValidateQRCode(string qrcode);
        Result ValidateOrderno(string orderno);
        Result ValidateTel(string tel);
    }
}

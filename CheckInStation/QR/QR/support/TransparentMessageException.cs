using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.support
{
    public class TransparentMessageException : Exception
    {
        public TransparentMessageException(string message) : base(message) { }

    }
}

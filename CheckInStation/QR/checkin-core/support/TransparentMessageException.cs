using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.support
{
    public class TransparentMessageException : Exception
    {
        public TransparentMessageException(string message) : base(message) { }

    }
}

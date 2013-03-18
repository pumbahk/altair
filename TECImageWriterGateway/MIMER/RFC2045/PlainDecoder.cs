using System;
using System.Collections.Generic;
using System.Text;

namespace MIMER.RFC2045
{
    class PlainDecoder: IDecoder
    {
        public bool CanDecode(string encoding)
        {
            return encoding == "7bit" || encoding == "8bit";
        }

        public byte[] Decode(System.IO.Stream dataStream)
        {
            throw new NotImplementedException();
        }

        public byte[] Decode(string data)
        {
            byte[] retval = new byte[data.Length];
            for (int i = 0; i < data.Length; i++)
            {
                retval[i] = (byte)data[i];
            }
            return retval;
        }
    }
}

using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;

namespace TECImageWriterGateway
{
    class Win32API
    {
        [DllImport("kernel32.dll", SetLastError=true)]
        private static extern uint GetSystemDirectory([Out] StringBuilder buf, uint uSize);

        public static string GetSystemDirectory()
        {
            StringBuilder retval = new StringBuilder(2047);
            uint len = GetSystemDirectory(retval, (uint)retval.Capacity);
            if (len == 0)
                return null;
            retval.Length = (int)len;
            return retval.ToString();
        }
    }
}

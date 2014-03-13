using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR.support
{
    public static class MachineName
    {
        public static string GetMachineName()
        {
            return System.Environment.MachineName;
        }

        public static string WithMachineName(this string fmt)
        {
            return String.Format("machine={0}: {1}", MachineName.GetMachineName(), fmt);
        }
    }
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.support
{
    public static class EnvironmentName
    {
        public static string GetMachineName()
        {
            return System.Environment.MachineName;
        }

        public static string WithMachineName(this string fmt)
        {
            return String.Format("machine={0}: {1}", EnvironmentName.GetMachineName(), fmt);
        }
    }
}

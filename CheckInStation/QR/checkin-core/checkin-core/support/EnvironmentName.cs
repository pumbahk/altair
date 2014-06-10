using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace QR.support
{
    public static class EnvironmentName
    {
        public static string GetMachineName()
        {
            return System.Environment.MachineName;
        }

        public static string GetApplicationInformationalVersion()
        {
            var assembly = Assembly.GetExecutingAssembly();
            var attribute = assembly.GetCustomAttributes(typeof(AssemblyInformationalVersionAttribute), true).FirstOrDefault() as AssemblyInformationalVersionAttribute;
            return attribute.InformationalVersion.Substring(0, "0.0.0.".Length+7);
        }

        public static string WithMachineName(this string fmt)
        {
            return String.Format("machine={0}: {1}", EnvironmentName.GetMachineName(), fmt);
        }
    }
}
